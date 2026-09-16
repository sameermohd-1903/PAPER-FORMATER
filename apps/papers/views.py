import os
import json

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db import transaction
from django.views.decorators.http import require_POST
from apps.questions.embedding_service import generate_embedding
from django.views.decorators.http import require_POST
from apps.questions.similarity_service import cosine_similarity
from apps.questions.quality_service import check_paper_quality
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import (
    PaperPattern,
    PatternSection,
    PatternQuestionSetting,
    GeneratedPaper,
    GeneratedQuestion,
)

from .forms import PaperPatternForm
from .services import PaperGeneratorService
from .serializers import (
    PaperPatternSerializer,
    GeneratedPaperSerializer,
)


# =========================================================
# HOME
# =========================================================

def home(request):
    return HttpResponse("Paper Formatter Home Page")


# =========================================================
# PAPER PATTERN LIST
# =========================================================

@login_required
def pattern_list(request):

    patterns = (
        PaperPattern.objects
        .filter(teacher=request.user)
        .order_by("-id")
    )

    return render(
        request,
        "papers/pattern_list.html",
        {
            "patterns": patterns
        }
    )


# =========================================================
# PATTERN BUILDER
# =========================================================

@login_required
def pattern_builder(request, pattern_id):

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    sections = (
        pattern.sections
        .prefetch_related("question_settings")
        .order_by("display_order")
    )

    return render(
        request,
        "papers/pattern_builder.html",
        {
            "pattern": pattern,
            "sections": sections,
        }
    )


# =========================================================
# ATTEMPT RULE HELPERS
# =========================================================

def get_available_question_count(attempt_rule):

    counts = {
        "1of2": 2,
        "2of3": 3,
        "3of4": 4,
        "4of5": 5,
        "5of5": 5,
        "all": 1,
    }

    return counts.get(attempt_rule, 0)


def get_attempted_question_count(attempt_rule):

    counts = {
        "1of2": 1,
        "2of3": 2,
        "3of4": 3,
        "4of5": 4,
        "5of5": 5,
        "all": 1,
    }

    return counts.get(attempt_rule, 0)


# =========================================================
# CREATE PATTERN
# =========================================================

@login_required
@transaction.atomic
def create_pattern(request):

    if request.method == "POST":

        form = PaperPatternForm(request.POST)

        # -------------------------------------------------
        # FORM VALIDATION
        # -------------------------------------------------

        if not form.is_valid():

            messages.error(
                request,
                "Please correct the errors in the paper information."
            )

            print("========== FORM INVALID ==========")
            print("FORM ERRORS:", form.errors)
            print("POST DATA:", request.POST)

            return render(
                request,
                "papers/create_pattern.html",
                {
                    "form": form
                }
            )

        # -------------------------------------------------
        # GET ROW DATA
        # -------------------------------------------------

        question_numbers = request.POST.getlist(
            "question_number[]"
        )

        attempt_rules = request.POST.getlist(
            "attempt_rule[]"
        )

        question_types = request.POST.getlist(
            "question_type[]"
        )

        marks_list = request.POST.getlist(
            "marks[]"
        )

        settings_list = request.POST.getlist(
            "question_settings[]"
        )

        # -------------------------------------------------
        # CHECK ROWS
        # -------------------------------------------------

        if not question_numbers:

            messages.error(
                request,
                "Please add at least one pattern row."
            )

            return render(
                request,
                "papers/create_pattern.html",
                {
                    "form": form
                }
            )

        # -------------------------------------------------
        # CHECK DATA LENGTH
        # -------------------------------------------------

        if not (
            len(question_numbers)
            == len(attempt_rules)
            == len(question_types)
            == len(marks_list)
        ):

            messages.error(
                request,
                "Invalid pattern row data."
            )

            return render(
                request,
                "papers/create_pattern.html",
                {
                    "form": form
                }
            )

        # -------------------------------------------------
        # VALIDATE MARKS
        # -------------------------------------------------

        marks_values = []

        try:

            for value in marks_list:

                marks = int(value)

                if marks <= 0:
                    raise ValueError

                marks_values.append(marks)

        except (ValueError, TypeError):

            messages.error(
                request,
                "Please enter valid Marks / Question for every row."
            )

            return render(
                request,
                "papers/create_pattern.html",
                {
                    "form": form
                }
            )

        # -------------------------------------------------
        # TEACHER ENTERED TOTAL MARKS
        # -------------------------------------------------

        teacher_total_marks = int(
            form.cleaned_data["total_marks"]
        )

        # -------------------------------------------------
        # CALCULATE ACTUAL PAPER MARKS
        # -------------------------------------------------

        calculated_total_marks = 0

        for index, attempt_rule in enumerate(
            attempt_rules
        ):

            attempted_questions = (
                get_attempted_question_count(
                    attempt_rule
                )
            )

            calculated_total_marks += (
                marks_values[index]
                * attempted_questions
            )

        # -------------------------------------------------
        # IMPORTANT:
        # TEACHER TOTAL MUST EQUAL CALCULATED TOTAL
        # -------------------------------------------------

        if calculated_total_marks != teacher_total_marks:

            messages.error(
                request,
                (
                    f"Total marks mismatch. "
                    f"Paper Total = {teacher_total_marks}, "
                    f"but Pattern Total = {calculated_total_marks}. "
                    f"Please adjust Marks / Question or Attempt Rule."
                )
            )

            return render(
                request,
                "papers/create_pattern.html",
                {
                    "form": form
                }
            )

        # =================================================
        # CREATE PAPER PATTERN
        # =================================================

        pattern = form.save(commit=False)

        pattern.teacher = request.user

        pattern.save()

        # =================================================
        # CREATE PATTERN SECTIONS
        # =================================================

        for index, question_number in enumerate(
            question_numbers
        ):

            attempt_rule = attempt_rules[index]

            question_type = question_types[index]

            marks = marks_values[index]

            available_questions = (
                get_available_question_count(
                    attempt_rule
                )
            )

            # -------------------------------------------------
            # QUESTION SETTINGS
            # -------------------------------------------------

            settings_data = []

            if index < len(settings_list):

                try:

                    settings_data = json.loads(
                        settings_list[index]
                    )

                    if not isinstance(
                        settings_data,
                        list
                    ):
                        settings_data = []

                except (
                    ValueError,
                    TypeError,
                    json.JSONDecodeError
                ):

                    settings_data = []

            # -------------------------------------------------
            # FILL MISSING SETTINGS
            # -------------------------------------------------

            while len(settings_data) < available_questions:

                settings_data.append(
                    {
                        "slot_number":
                            len(settings_data) + 1,

                        "unit":
                            "",

                        "bloom_level":
                            "1",

                        "co":
                            "CO1",

                        "difficulty":
                            "Easy",
                    }
                )

            settings_data = settings_data[
                :available_questions
            ]

            # -------------------------------------------------
            # FIRST SETTING
            # -------------------------------------------------

            first_setting = (
                settings_data[0]
                if settings_data
                else {
                    "unit": "",
                    "bloom_level": "1",
                    "co": "CO1",
                    "difficulty": "Easy",
                }
            )

            # =================================================
            # CREATE SECTION
            # =================================================

            section = PatternSection.objects.create(

                pattern=pattern,

                display_order=index + 1,

                question_number=question_number,

                attempt_rule=attempt_rule,

                custom_attempt_text="",

                unit="",

                bloom_level=str(
                    first_setting.get(
                        "bloom_level",
                        "1"
                    )
                ),

                co=first_setting.get(
                    "co",
                    "CO1"
                ),

                difficulty=first_setting.get(
                    "difficulty",
                    "Easy"
                ),

                question_type=question_type,

                marks=marks,

                number_of_questions=(
                    available_questions
                ),
            )

            # =================================================
            # CREATE QUESTION SETTINGS
            # =================================================

            for slot_number in range(
                1,
                available_questions + 1
            ):

                setting = settings_data[
                    slot_number - 1
                ]

                # -------------------------------------------------
                # GET INDIVIDUAL UNIT
                # -------------------------------------------------

                unit = str(
                    setting.get(
                        "unit",
                        ""
                    )
                    or ""
                ).strip()

                # -------------------------------------------------
                # GET BLOOM
                # -------------------------------------------------

                bloom_level = str(
                    setting.get(
                        "bloom_level",
                        "1"
                    )
                    or "1"
                ).strip()

                # -------------------------------------------------
                # GET CO
                # -------------------------------------------------

                co = str(
                    setting.get(
                        "co",
                        "CO1"
                    )
                    or "CO1"
                ).strip()

                # -------------------------------------------------
                # GET DIFFICULTY
                # -------------------------------------------------

                difficulty = str(
                    setting.get(
                        "difficulty",
                        "Easy"
                    )
                    or "Easy"
                ).strip().lower()

                # =================================================
                # SAVE QUESTION SETTING
                # =================================================

                PatternQuestionSetting.objects.create(

                    section=section,

                    slot_number=slot_number,

                    unit=unit,

                    bloom_level=bloom_level,

                    co=co,

                    difficulty=difficulty,
                )

        # =================================================
        # SUCCESS
        # =================================================

        messages.success(
            request,
            "Pattern created successfully."
        )

        print("================================")
        print("PATTERN CREATED SUCCESSFULLY")
        print("Pattern ID:", pattern.id)
        print("Pattern Name:", pattern.pattern_name)
        print("Total Marks:", pattern.total_marks)
        print("================================")

        return redirect(
            "papers:pattern_builder",
            pattern_id=pattern.id
        )

    # =====================================================
    # GET
    # =====================================================

    form = PaperPatternForm()

    return render(
        request,
        "papers/create_pattern.html",
        {
            "form": form
        }
    )


# =========================================================
# SAVE PATTERN BUILDER ROWS
# =========================================================

@login_required
@require_POST
@transaction.atomic
def save_pattern_rows(request, pattern_id):
    import json

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    try:
        data = json.loads(request.body)
        rows = data.get("rows", [])

        if not rows:
            return JsonResponse({
                "success": False,
                "message": "No pattern rows received."
            }, status=400)

        # =====================================================
        # DELETE OLD SECTIONS
        # =====================================================

        pattern.sections.all().delete()

        # =====================================================
        # CREATE NEW SECTIONS
        # =====================================================

        for row_index, row in enumerate(rows, start=1):

            question_number = (
                row.get("question_number")
                or f"Q{row_index}"
            )

            attempt_rule = (
                row.get("attempt_rule")
                or ""
            )

            custom_attempt_text = (
                row.get("custom_attempt_text")
                or ""
            )

            question_type = (
                row.get("question_type")
                or "mcq"
            )

            marks = int(
                row.get("marks") or 0
            )

            number_of_questions = int(
                row.get("number_of_questions") or 0
            )

            question_settings = (
                row.get("question_settings")
                or []
            )
            question_settings = (
                row.get("question_settings")
                or []
            )

            print("\n====================================")
            print("SAVE PATTERN DEBUG")
            print("Question:", question_number)
            print("Question Settings Received:")
            print(question_settings)
            print("====================================\n")

            # =================================================
            # VALIDATE BASIC VALUES
            # =================================================

            if not attempt_rule:
                return JsonResponse({
                    "success": False,
                    "message":
                        f"Please select Attempt Rule for {question_number}."
                }, status=400)

            if marks <= 0:
                return JsonResponse({
                    "success": False,
                    "message":
                        f"Please enter valid marks for {question_number}."
                }, status=400)

            if number_of_questions <= 0:
                return JsonResponse({
                    "success": False,
                    "message":
                        f"Invalid number of questions for {question_number}."
                }, status=400)

            # =================================================
            # VALIDATE SETTINGS COUNT
            # =================================================

            if len(question_settings) != number_of_questions:
                return JsonResponse({
                    "success": False,
                    "message":
                        f"{question_number} requires "
                        f"{number_of_questions} question settings, "
                        f"but received {len(question_settings)}."
                }, status=400)

            # =================================================
            # CREATE SECTION
            # =================================================

            section = PatternSection.objects.create(

                pattern=pattern,

                display_order=row_index,

                question_number=question_number,

                attempt_rule=attempt_rule,

                custom_attempt_text=custom_attempt_text,

                # -------------------------------------------------
                # IMPORTANT:
                # Unit is NOT stored at section level anymore.
                # Every question setting has its own Unit.
                # -------------------------------------------------

                unit="",

                # These are kept for compatibility with the
                # existing PatternSection model.
                bloom_level="1",

                co="CO1",

                difficulty="easy",

                question_type=question_type,

                marks=marks,

                number_of_questions=number_of_questions,
            )

            # =================================================
            # CREATE INDIVIDUAL QUESTION SETTINGS
            # =================================================

            for setting_index, setting in enumerate(
                question_settings,
                start=1
            ):

                slot_number = int(
                    setting.get("slot_number")
                    or setting_index
                )

                unit = str(
                    setting.get("unit")
                    or ""
                ).strip()

                bloom_level = str(
                    setting.get("bloom_level")
                    or "1"
                ).strip()

                co = str(
                    setting.get("co")
                    or "CO1"
                ).strip()

                difficulty = str(
                    setting.get("difficulty")
                    or "easy"
                ).strip().lower()

                # =================================================
                # VALIDATE BLOOM
                # =================================================

                if bloom_level not in [
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6"
                ]:
                    return JsonResponse({
                        "success": False,
                        "message":
                            f"Invalid Bloom Level in "
                            f"{question_number}, Question {slot_number}."
                    }, status=400)

                # =================================================
                # VALIDATE DIFFICULTY
                # =================================================

                if difficulty not in [
                    "easy",
                    "medium",
                    "hard"
                ]:
                    return JsonResponse({
                        "success": False,
                        "message":
                            f"Invalid difficulty in "
                            f"{question_number}, Question {slot_number}."
                    }, status=400)

                # =================================================
                # CREATE QUESTION SETTING
                # =================================================

                PatternQuestionSetting.objects.create(

                    section=section,

                    slot_number=slot_number,

                    # ---------------------------------------------
                    # INDIVIDUAL UNIT
                    # ---------------------------------------------

                    unit=unit,

                    # ---------------------------------------------
                    # BLOOM
                    # ---------------------------------------------

                    bloom_level=bloom_level,

                    # ---------------------------------------------
                    # CO
                    # ---------------------------------------------

                    co=co or "CO1",

                    # ---------------------------------------------
                    # DIFFICULTY
                    # ---------------------------------------------

                    difficulty=difficulty,
                )

        # =====================================================
        # SUCCESS
        # =====================================================

        return JsonResponse({
            "success": True,
            "message": "Pattern saved successfully."
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid JSON data."
        }, status=400)

    except ValueError:
        return JsonResponse({
            "success": False,
            "message": "Invalid numeric value received."
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)


# =========================================================
# LOAD PATTERN ROWS
# =========================================================

@login_required
def load_pattern_rows(
    request,
    pattern_id
):

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    rows = []

    sections = (
        pattern.sections
        .prefetch_related(
            "question_settings"
        )
        .order_by(
            "display_order"
        )
    )

    for section in sections:

        settings_data = []

        for setting in (
            section.question_settings.all()
        ):

            settings_data.append(
                {
                    "slot_number":
                        setting.slot_number,
                    "unit":    
                        setting.unit,

                    "bloom_level":
                        setting.bloom_level,

                    "co":
                        setting.co,

                    "difficulty":
                        setting.difficulty,
                }
            )

        rows.append(
            {
                "id":
                    section.id,

                "display_order":
                    section.display_order,

                "question_number":
                    section.question_number,

                "attempt_rule":
                    section.attempt_rule,

                "question_type":
                    section.question_type,

                "marks":
                    section.marks,

                "number_of_questions":
                    section.number_of_questions,

                "question_settings":
                    settings_data,
            }
        )

    return JsonResponse(
        {
            "rows": rows,

            "total_marks":
                pattern.total_marks,
        }
    )


# =========================================================
# GET PATTERN ROWS
# Compatibility API
# =========================================================

@login_required
def get_pattern_rows(
    request,
    pattern_id
):

    return load_pattern_rows(
        request,
        pattern_id
    )


# =========================================================
# PREPARE PREVIEW CONTEXT
# =========================================================

# =========================================================
# PREPARE PREVIEW CONTEXT
# =========================================================

def _prepare_pattern_context(pattern, teacher):
    
    from apps.questions.models import Question
    from apps.questions.question_selection_service import select_best_question

    sections = list(
        pattern.sections
        .prefetch_related("question_settings")
        .order_by("display_order")
    )

    letters = [
        "a", "b", "c", "d", "e",
        "f", "g", "h", "i", "j"
    ]

    # =========================================================
    # GET / CREATE DRAFT GENERATED PAPER
    # =========================================================

    paper, _ = GeneratedPaper.objects.get_or_create(
        pattern=pattern,
        teacher=teacher,
        defaults={
            "title": f"{pattern.pattern_name} Question Paper"
        }
    )

    # =========================================================
    # CURRENT ASSIGNMENTS
    # =========================================================

    assigned_gqs = list(
        GeneratedQuestion.objects
        .filter(paper=paper)
        .select_related("question", "section")
        .order_by("display_order")
    )

    assigned_map = {
        (gq.section_id, gq.display_order): gq
        for gq in assigned_gqs
    }
    validation_errors = []

    # =========================================================
    # PROCESS EVERY SECTION
    # =========================================================

    for section in sections:

        settings = list(
            section.question_settings
            .all()
            .order_by("slot_number")
        )

        row_count = section.number_of_questions

        section.subparts = letters[:row_count]

        # -----------------------------------------------------
        # MAKE SURE SETTINGS EXIST
        # -----------------------------------------------------

        if len(settings) < row_count:

            raise ValueError(
                f"{section.question_number} has "
                f"{len(settings)} settings but requires "
                f"{row_count} questions."
            )

        # =====================================================
        # PROCESS EVERY QUESTION SLOT
        # =====================================================

        for index in range(row_count):

            setting = settings[index]

            display_order = index + 1

            existing_gq = assigned_map.get(
                (section.id, display_order)
            )

            # =================================================
            # SLOT SETTINGS
            # =================================================

            unit = str(
                getattr(setting, "unit", "") or ""
            ).strip()

            difficulty = str(
                setting.difficulty or ""
            ).strip().lower()

            bloom_level = str(
                setting.bloom_level or ""
            ).strip()

            question_type = str(
                section.question_type or ""
            ).strip().lower()

            marks = section.marks

            # =================================================
            # BASE ELIGIBILITY
            #
            # HARD RULES:
            #
            # SAME TEACHER
            # SAME PROGRAM
            # SAME SEMESTER
            # SAME SUBJECT
            # SAME MARKS
            # SAME DIFFICULTY
            # SAME UNIT WHEN SPECIFIED
            #
            # BLOOM + QUESTION TYPE = RANKING PREFERENCE
            # =================================================

            queryset = Question.objects.filter(
                teacher=teacher,
                is_active=True,
                program=pattern.program,
                semester=pattern.semester,
                subject=pattern.subject,
                marks=marks,
                difficulty__iexact=difficulty,
                question_type__iexact=question_type,
            )

            # =================================================
            # UNIT FILTER
            # =================================================

            if unit:

                queryset = queryset.filter(
                    unit__iexact=unit
                )
                
            if bloom_level:
                queryset = queryset.filter(
                    bloom_level__iexact=bloom_level
                )    

            # =================================================
            # GET QUESTIONS ALREADY USED IN THIS PAPER
            #
            # Current slot is excluded because its existing
            # question may remain in the same slot.
            # =================================================

            used_question_ids = set(
                GeneratedQuestion.objects
                .filter(paper=paper)
                .exclude(
                    pk=(
                        existing_gq.pk
                        if existing_gq
                        else None
                    )
                )
                .values_list(
                    "question_id",
                    flat=True
                )
            )

            # =================================================
            # REMOVE QUESTIONS ALREADY USED ELSEWHERE
            # =================================================

            if used_question_ids:

                queryset = queryset.exclude(
                    id__in=used_question_ids
                )

            # =================================================
            # CHECK EXISTING QUESTION
            # =================================================

            if existing_gq:

                existing_question = existing_gq.question

                # -------------------------------------------------
                # NORMALIZE EXISTING VALUES
                # -------------------------------------------------

                existing_difficulty = str(
                    existing_question.difficulty or ""
                ).strip().lower()

                existing_bloom = str(
                    existing_question.bloom_level or ""
                ).strip()

                existing_type = str(
                    existing_question.question_type or ""
                ).strip().lower()

                required_type = str(
                    question_type or ""
                ).strip().lower()

                # -------------------------------------------------
                # NORMALIZE LEGACY CASE STUDY VALUE
                # -------------------------------------------------

                if existing_type == "cs":
                    existing_type = "casestudy"

                if required_type == "cs":
                    required_type = "casestudy"

                # =================================================
                # HARD CONSTRAINT VALIDATION
                # =================================================

                existing_valid = (
                    existing_question.teacher_id == teacher.id
                    and existing_question.is_active
                    and existing_question.program_id == pattern.program_id
                    and existing_question.semester_id == pattern.semester_id
                    and existing_question.subject_id == pattern.subject_id
                    and existing_question.marks == marks
                    and existing_difficulty == difficulty
                )

                # =================================================
                # CHECK UNIT
                # =================================================

                if unit:

                    existing_valid = (
                        existing_valid
                        and
                        str(
                            existing_question.unit or ""
                        ).strip().lower()
                        == unit.lower()
                    )

                # =================================================
                # MANUAL REPLACEMENT CHECK
                #
                # If teacher manually selected this question,
                # Bloom and Question Type are NOT checked.
                #
                # Only HARD constraints above are important.
                # =================================================

                if existing_gq.is_manual_replacement:

                    if existing_valid:

                        # Keep the teacher's selected question.
                        continue

                    # Manual replacement no longer satisfies
                    # a hard constraint, so remove it.

                    existing_gq.delete()

                    assigned_map.pop(
                        (section.id, display_order),
                        None
                    )

                else:

                    # =================================================
                    # AUTOMATICALLY GENERATED QUESTION
                    #
                    # Bloom and Question Type are preferences.
                    # If they don't match, regenerate.
                    # =================================================

                    if bloom_level:

                        existing_valid = (
                            existing_valid
                            and
                            existing_bloom
                            == bloom_level
                        )

                    if required_type:

                        existing_valid = (
                            existing_valid
                            and
                            existing_type
                            == required_type
                        )

                    # =================================================
                    # EXISTING AUTOMATIC QUESTION IS VALID
                    # =================================================

                    if existing_valid:

                        continue

                    # =================================================
                    # EXISTING AUTOMATIC QUESTION IS INVALID
                    # =================================================

                    existing_gq.delete()

                    assigned_map.pop(
                        (section.id, display_order),
                        None
                    )

            # =================================================
            # FIND AVAILABLE QUESTIONS
            # =================================================

            available_questions = list(
                queryset
            )

            # =================================================
            # NO QUESTION AVAILABLE
            # =================================================

            if not available_questions:
    
                validation_errors.append({
                    "section": section.question_number,
                    "slot": setting.slot_number,
                    "unit": unit if unit else "All Units",
                    "marks": marks,
                    "difficulty": difficulty,
                    "bloom_level": bloom_level,
                    "question_type": question_type,
                    "message": (
                        f"No matching question is available for "
                        f"{section.question_number}, Question {setting.slot_number}."
                    ),
                })

                continue

            # =================================================
            # AI-ASSISTED QUESTION SELECTION
            # =================================================
            #
            # Django already applied HARD constraints.
            #
            # Ranking considers:
            #
            # 1. Bloom match
            # 2. Question type match
            # 3. Semantic similarity when a reference exists
            #
            # For a new slot, reference_question=None.
            # =================================================
            
            
            # =================================================
            # CREATE SEMANTIC REFERENCE
            # =================================================

            reference_text = (
                f"Subject: {pattern.subject.name}. "
                f"Unit {unit if unit else 'All Units'}. "
                f"Bloom level {bloom_level}. "
                f"{difficulty} difficulty. "
                f"{question_type} question."
            )

            try:

                reference_embedding = generate_embedding(
                    reference_text
                )

            except Exception:

                reference_embedding = None
                
                
                
                
                
            
            
            
            

            selection = select_best_question(
                questions=available_questions,
                required_bloom_level=bloom_level,
                required_question_type=question_type,
                reference_question=None,
                reference_embedding=reference_embedding
            )

            # =================================================
            # SAFETY CHECK
            # =================================================

            if not selection:
                validation_errors.append({
                    "section": section.question_number,
                    "slot": setting.slot_number,
                    "unit": unit if unit else "All Units",
                    "marks": marks,
                    "difficulty": difficulty,
                    "bloom_level": bloom_level,
                    "question_type": question_type,
                    "message": (
                        f"No matching question is available for "
                        f"{section.question_number}, Question {setting.slot_number}."
                    ),
                })
                continue

            # =================================================
            # GET SELECTED QUESTION
            # =================================================

            selected_question = selection["question"]

            # =================================================
            # CREATE GENERATED QUESTION
            # =================================================
            
            print(
                f"""
            ====================================
            AI QUESTION SELECTION
            Section: {section.question_number}
            Slot: {setting.slot_number}

            Selected Question ID: {selected_question.id}
            Score: {selection['score']}
            Similarity: {selection['similarity']}
            Bloom Match: {selection['bloom_match']}
            Type Match: {selection['type_match']}
====================================
            """
            )

            new_gq = GeneratedQuestion.objects.create(
                paper=paper,
                section=section,
                question=selected_question,
                display_order=display_order
            )

            assigned_map[
                (section.id, display_order)
            ] = new_gq

    # =========================================================
    # BUILD TEMPLATE DATA
    # =========================================================

    assigned_gqs = list(
        GeneratedQuestion.objects
        .filter(paper=paper)
        .select_related("question", "section")
        .order_by("display_order")
    )

    generated_map = {
        (gq.section_id, gq.display_order):
            gq.question
        for gq in assigned_gqs
    }

    # =========================================================
    # SUBPART DATA
    # =========================================================

    for section in sections:

        subparts_data = []

        for index, letter in enumerate(
            section.subparts
        ):

            display_order = index + 1

            question = generated_map.get(
                (
                    section.id,
                    display_order
                )
            )

            subparts_data.append({
                "letter": letter,
                "display_order": display_order,
                "question": question,
            })

        section.subparts_data = subparts_data

    # =========================================================
    # RETURN CONTEXT
    # =========================================================

    return {
        "pattern": pattern,
        "sections": sections,
        "paper": paper,
        "validation_errors": validation_errors,
    }



# =========================================================
# PAPER PREVIEW - PATTERN
# =========================================================

@login_required
def paper_preview_pattern(request, pattern_id):
    """
    Preview a paper pattern.

    Questions are automatically generated by
    _prepare_pattern_context().
    """

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    context = _prepare_pattern_context(
        pattern,
        request.user
    )

    return render(
        request,
        "papers/paper_preview.html",
        context
    )


# =========================================================
# DELETE PATTERN
# =========================================================

@login_required
@require_POST
@transaction.atomic
def delete_pattern(
    request,
    pattern_id
):

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    pattern_name = pattern.pattern_name

    # -----------------------------------------------------
    # DELETE GENERATED QUESTION/PAPER DATA FIRST
    # -----------------------------------------------------

    generated_papers = (
        GeneratedPaper.objects
        .filter(
            pattern=pattern,
            teacher=request.user
        )
    )

    for paper in generated_papers:

        GeneratedQuestion.objects.filter(
            paper=paper
        ).delete()

    generated_papers.delete()

    # -----------------------------------------------------
    # PATTERN SECTIONS
    # -----------------------------------------------------

    pattern.sections.all().delete()

    # -----------------------------------------------------
    # DELETE PATTERN
    # -----------------------------------------------------

    pattern.delete()

    messages.success(
        request,
        f'Pattern "{pattern_name}" deleted successfully.'
    )

    return redirect(
        "papers:pattern_list"
    )


# =========================================================
# PRINT
# =========================================================

@login_required
def paper_print(
    request,
    pattern_id
):

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    context = _prepare_pattern_context(
        pattern,
        request.user
    )

    return render(
        request,
        "papers/paper_print.html",
        context
    )


# =========================================================
# PDF
# =========================================================

@login_required
def paper_pdf(request, pattern_id):

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    # Make sure all questions are generated/assigned
    context = _prepare_pattern_context(
        pattern,
        request.user
    )
    
    # =========================================================
    # BLOCK PDF GENERATION IF QUESTIONS ARE MISSING
    # =========================================================

    if context.get("validation_errors"):

        messages.error(
            request,
            "Paper cannot be generated because some question "
            "requirements do not have matching questions."
        )

        return redirect(
            "papers:paper_preview_pattern",
            pattern_id=pattern.id
        )

    from apps.formatter.pdf_generator import PDFGenerator

    try:
        pdf_path = PDFGenerator.generate_pattern_pdf(
            pattern,
            context
        )

        from django.http import FileResponse

        full_path = os.path.join(
            settings.MEDIA_ROOT,
            pdf_path
        )

        response = FileResponse(
            open(full_path, "rb"),
            content_type="application/pdf"
        )

        response["Content-Disposition"] = (
            f'attachment; filename="'
            f'{pattern.pattern_name}.pdf"'
        )

        return response

    except Exception as error:

        messages.error(
            request,
            f"PDF generation failed: {error}"
        )

        return redirect(
            "papers:paper_preview_pattern",
            pattern_id=pattern.id
        )


# =========================================================
# SECTION QUESTIONS API
# =========================================================

@login_required
def get_section_questions_api(request, pattern_id, section_id):

    from apps.questions.models import Question
    from apps.questions.question_selection_service import rank_questions
    from apps.questions.similarity_service import cosine_similarity

    # =========================================================
    # GET PATTERN
    # =========================================================

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    # =========================================================
    # GET SECTION
    # =========================================================

    section = get_object_or_404(
        PatternSection,
        id=section_id,
        pattern=pattern
    )

    # =========================================================
    # GET / CREATE GENERATED PAPER
    # =========================================================

    paper, _ = GeneratedPaper.objects.get_or_create(
        pattern=pattern,
        teacher=request.user,
        defaults={
            "title": f"{pattern.pattern_name} Question Paper"
        }
    )

    # =========================================================
    # CURRENTLY ASSIGNED QUESTIONS
    # =========================================================

    assigned_gqs = list(
        GeneratedQuestion.objects
        .filter(paper=paper)
        .select_related(
            "question",
            "section"
        )
        .order_by("display_order")
    )

    # =========================================================
    # ALL QUESTION IDS ALREADY USED IN PAPER
    # =========================================================

    used_question_ids = {
        gq.question_id
        for gq in assigned_gqs
        if gq.question_id
    }

    # =========================================================
    # CURRENT SECTION ASSIGNMENTS
    # =========================================================

    current_section_gqs = {
        gq.display_order: gq.question
        for gq in assigned_gqs
        if gq.section_id == section.id
    }

    # =========================================================
    # INDIVIDUAL SLOT SETTINGS
    # =========================================================

    settings = list(
        section.question_settings
        .all()
        .order_by("slot_number")
    )

    letters = [
        "a", "b", "c", "d", "e",
        "f", "g", "h", "i", "j"
    ]

    slots = []

    # =========================================================
    # PROCESS EVERY QUESTION SLOT
    # =========================================================

    for index in range(section.number_of_questions):

        slot_number = index + 1

        # -----------------------------------------------------
        # FIND SETTING FOR THIS SLOT
        # -----------------------------------------------------

        setting = next(
            (
                s
                for s in settings
                if s.slot_number == slot_number
            ),
            None
        )

        # -----------------------------------------------------
        # CURRENT QUESTION
        # -----------------------------------------------------

        current_question = current_section_gqs.get(
            slot_number
        )

        # -----------------------------------------------------
        # SLOT SETTINGS
        # -----------------------------------------------------

        if setting:

            unit = str(
                getattr(setting, "unit", "") or ""
            ).strip()

            bloom_level = str(
                setting.bloom_level or ""
            ).strip()

            difficulty = str(
                setting.difficulty or ""
            ).strip().lower()

        else:

            unit = ""
            bloom_level = ""
            difficulty = ""

        # =====================================================
        # CANDIDATE QUESTIONS
        # =====================================================
        #
        # HARD RULES:
        #
        # SAME TEACHER
        # SAME PROGRAM
        # SAME SEMESTER
        # SAME SUBJECT
        # SAME MARKS
        # SAME DIFFICULTY
        #
        # UNIT:
        # SAME UNIT when a specific unit is selected
        #
        # BLOOM:
        # NOT a hard filter
        #
        # QUESTION TYPE:
        # NOT a hard filter
        #
        # =====================================================

        queryset = Question.objects.filter(

            teacher=request.user,

            is_active=True,

            program=pattern.program,

            semester=pattern.semester,

            subject=pattern.subject,

            marks=section.marks,

            difficulty__iexact=difficulty,
            
            # SAME QUESTION TYPE
            question_type__iexact=section.question_type,

            # SAME BLOOM LEVEL
            bloom_level__iexact=bloom_level,

        )

        # =====================================================
        # UNIT FILTER
        # =====================================================

        if unit:

            queryset = queryset.filter(
                unit__iexact=unit
            )

        # =====================================================
        # BUILD CANDIDATE IDS
        # =====================================================

        candidate_ids = set(
            queryset.values_list(
                "id",
                flat=True
            )
        )

        # =====================================================
        # CURRENT QUESTION
        # =====================================================
        #
        # Keep current question visible in the modal.
        # JavaScript will show it as "Current" and disable it.
        #
        # =====================================================

        if current_question:

            candidate_ids.add(
                current_question.id
            )

        # =====================================================
        # GET QUESTIONS
        # =====================================================

        all_questions = (
            Question.objects
            .filter(
                id__in=candidate_ids
            )
            .select_related(
                "program",
                "semester",
                "subject"
            )
        )

        # =====================================================
        # CURRENT QUESTION EMBEDDING
        # =====================================================

        current_embedding = None

        if (
            current_question
            and current_question.embedding
        ):

            current_embedding = (
                current_question.embedding
            )

        # =====================================================
        # QUESTION DATA
        # =====================================================

        # =====================================================
        # AI RANKING
        # =====================================================

        ranked_questions = rank_questions(
           questions=all_questions,
            required_bloom_level=bloom_level,
           required_question_type=section.question_type,
           reference_question=current_question,
        )

        question_data = []

        for item in ranked_questions:

            question = item["question"]

            # -------------------------------------------------
            # IS CURRENT QUESTION?
            # -------------------------------------------------

            is_current = (

                current_question is not None

                and

                question.id
                ==
                current_question.id

            )

            # -------------------------------------------------
            # IS USED ELSEWHERE IN PAPER?
            # -------------------------------------------------

            is_used = (

                question.id
                in used_question_ids

                and

                not is_current

            )

            # =================================================
            # AI SIMILARITY
            # =================================================

            similarity = round(
                item["similarity"] * 100,
                2
            )

            # =================================================
            # ADD QUESTION
            # =================================================

            question_data.append({

                "id":
                    question.id,

                "question_text":
                    question.question_text,

                "unit":
                    question.unit,

                "marks":
                    question.marks,

                # -------------------------------------------------
                # Bloom display
                # -------------------------------------------------

                "bloom_level":
                    question.get_bloom_level_display(),

                # -------------------------------------------------
                # Bloom numeric value
                # -------------------------------------------------

                "bloom_value":
                    question.bloom_level,

                # -------------------------------------------------
                # Difficulty display
                # -------------------------------------------------

                "difficulty":
                    question.get_difficulty_display(),

                # -------------------------------------------------
                # Difficulty database value
                # -------------------------------------------------

                "difficulty_value":
                    question.difficulty,

                # -------------------------------------------------
                # Question type
                # -------------------------------------------------

                "question_type":
                    (
                        question.get_question_type_display_name()

                        if hasattr(
                            question,
                            "get_question_type_display_name"
                        )

                        else
                        question.get_question_type_display()
                    ),

                # -------------------------------------------------
                # Question type database value
                # -------------------------------------------------

                "question_type_value":
                    question.question_type,

                # -------------------------------------------------
                # AI similarity percentage
                # -------------------------------------------------

                "similarity":
                    similarity,
                "score": item["score"],
                "bloom_match":
                    item["bloom_match"],
                "type_match":
                    item["type_match"],

                # -------------------------------------------------
                # Current question
                # -------------------------------------------------

                "is_current":
                    is_current,

                # -------------------------------------------------
                # Already used in paper
                # -------------------------------------------------

                "is_used":
                    is_used,

            })

        # =====================================================
        # SORT BY AI SIMILARITY
        # =====================================================
        #
        # Highest similarity appears first.
        #
        # Current question is kept at the bottom.
        #
        # =====================================================

       

        

        # =====================================================
        # ADD SLOT
        # =====================================================

        slots.append({

            "slot_index":
                index,

            "display_order":
                slot_number,

            "letter":
                letters[index],

            "question_id":
                (
                    current_question.id
                    if current_question
                    else None
                ),

            "question_text":
                (
                    current_question.question_text
                    if current_question
                    else None
                ),

            "unit":
                unit,

            "bloom_level":
                bloom_level,

            "difficulty":
                difficulty,

            "marks":
                section.marks,

            "question_type":
                section.question_type,

            "questions":
                question_data,

        })

    # =========================================================
    # RESPONSE
    # =========================================================

    return JsonResponse({

        "success":
            True,

        "section": {

            "id":
                section.id,

            "question_number":
                section.question_number,

            "marks":
                section.marks,

            "question_type":
                section.question_type,

            "number_of_questions":
                section.number_of_questions,

        },

        "slots":
            slots,

    })


# =========================================================
# ASSIGN QUESTION
# =========================================================

@login_required
@require_POST
@transaction.atomic
def assign_section_question_api(request, pattern_id):

    from apps.questions.models import Question

    # =========================================================
    # GET PATTERN
    # =========================================================

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    # =========================================================
    # READ REQUEST
    # =========================================================

    try:
        data = json.loads(request.body)

    except (json.JSONDecodeError, TypeError):

        return JsonResponse({
            "success": False,
            "message": "Invalid JSON."
        }, status=400)

    section_id = data.get("section_id")
    slot_index = data.get("slot_index")
    question_id = data.get("question_id")

    # =========================================================
    # VALIDATE BASIC DATA
    # =========================================================

    if section_id is None:
        return JsonResponse({
            "success": False,
            "message": "Section ID is required."
        }, status=400)

    if slot_index is None:
        return JsonResponse({
            "success": False,
            "message": "Slot index is required."
        }, status=400)

    if question_id is None:
        return JsonResponse({
            "success": False,
            "message": "Question ID is required."
        }, status=400)

    try:
        slot_index = int(slot_index)
        question_id = int(question_id)

    except (ValueError, TypeError):

        return JsonResponse({
            "success": False,
            "message": "Invalid section, slot or question ID."
        }, status=400)

    # =========================================================
    # GET SECTION
    # =========================================================

    section = get_object_or_404(
        PatternSection,
        id=section_id,
        pattern=pattern
    )

    # =========================================================
    # VALIDATE SLOT
    # =========================================================

    if slot_index < 0:
        return JsonResponse({
            "success": False,
            "message": "Invalid slot."
        }, status=400)

    display_order = slot_index + 1

    if display_order > section.number_of_questions:

        return JsonResponse({
            "success": False,
            "message": "Invalid question slot."
        }, status=400)

    # =========================================================
    # GET QUESTION
    # =========================================================

    question = get_object_or_404(
        Question,
        id=question_id,
        teacher=request.user
    )

    # =========================================================
    # GET SLOT SETTINGS
    # =========================================================

    setting = (
        PatternQuestionSetting.objects
        .filter(
            section=section,
            slot_number=display_order
        )
        .first()
    )

    if not setting:

        return JsonResponse({
            "success": False,
            "message":
                "Question settings for this slot were not found."
        }, status=400)

    # =========================================================
    # SLOT UNIT
    # =========================================================

    required_unit = str(
        getattr(setting, "unit", "") or ""
    ).strip()

    # =========================================================
    # SLOT DIFFICULTY
    # =========================================================

    required_difficulty = str(
        setting.difficulty or ""
    ).strip().lower()
    
    required_bloom = str(
        setting.bloom_level or ""
    ).strip()

    required_type = str(
        section.question_type or ""
    ).strip().lower()

    if required_type == "cs":
        required_type = "casestudy"

    question_type = str(
    question.question_type or ""
    ).strip().lower()

    if question_type == "cs":
        question_type = "casestudy"

    # =========================================================
    # RULE 1 — SAME PROGRAM
    # =========================================================

    if question.program_id != pattern.program_id:

        return JsonResponse({
            "success": False,
            "message":
                "Replacement question must belong to the same program."
        }, status=400)

    # =========================================================
    # RULE 2 — SAME SEMESTER
    # =========================================================

    if question.semester_id != pattern.semester_id:

        return JsonResponse({
            "success": False,
            "message":
                "Replacement question must belong to the same semester."
        }, status=400)

    # =========================================================
    # RULE 3 — SAME SUBJECT
    # =========================================================

    if question.subject_id != pattern.subject_id:

        return JsonResponse({
            "success": False,
            "message":
                "Replacement question must belong to the same subject."
        }, status=400)

    # =========================================================
    # RULE 4 — SAME MARKS
    # =========================================================

    if question.marks != section.marks:

        return JsonResponse({
            "success": False,
            "message":
                "Replacement question must have the same marks."
        }, status=400)

    # =========================================================
    # RULE 5 — SAME DIFFICULTY
    # =========================================================

    if (
        str(question.difficulty or "").strip().lower()
        != required_difficulty
    ):

        return JsonResponse({
            "success": False,
            "message":
                "Replacement question must have the same difficulty."
        }, status=400)
        
    # =========================================================
    # RULE 6 — SAME BLOOM LEVEL
    # =========================================================

    if required_bloom:

        question_bloom = str(
            question.bloom_level or ""
        ).strip()

        if question_bloom != required_bloom:

            return JsonResponse({
                "success": False,
                "message":
                    "Replacement question must have the same Bloom level."
            }, status=400)    
    
    
    # =========================================================
    # RULE 7 — SAME QUESTION TYPE
    # =========================================================

    if required_type:

        if question_type != required_type:

            return JsonResponse({
                "success": False,
                "message":
                    "Replacement question must have the same question type."
            }, status=400)
    
        
        

    # =========================================================
    # RULE 6 — SAME UNIT
    # =========================================================
    #
    # If the slot has a specific unit:
    # replacement MUST have that unit.
    #
    # If slot unit is empty:
    # any unit is allowed.
    #
    # =========================================================

    if required_unit:

        question_unit = str(
            question.unit or ""
        ).strip()

        if question_unit.lower() != required_unit.lower():

            return JsonResponse({
                "success": False,
                "message":
                    "Replacement question must belong to the same unit."
            }, status=400)

    # =========================================================
    # GET / CREATE GENERATED PAPER
    # =========================================================

    paper, _ = GeneratedPaper.objects.get_or_create(

        pattern=pattern,

        teacher=request.user,

        defaults={
            "title":
                f"{pattern.pattern_name} Question Paper"
        }
    )

    # =========================================================
    # CURRENT QUESTION IN THIS SLOT
    # =========================================================

    current_gq = (
        GeneratedQuestion.objects
        .filter(
            paper=paper,
            section=section,
            display_order=display_order
        )
        .first()
    )

    # =========================================================
    # DON'T SELECT THE SAME QUESTION
    # =========================================================

    if (
        current_gq
        and
        current_gq.question_id == question.id
    ):

        return JsonResponse({
            "success": False,
            "message":
                "This question is already assigned to this slot."
        }, status=400)

    # =========================================================
    # RULE 7 — QUESTION MUST NOT ALREADY BE USED
    # =========================================================
    #
    # Exclude the current slot because its question is allowed
    # to be replaced.
    #
    # =========================================================

    already_used = (
        GeneratedQuestion.objects
        .filter(
            paper=paper,
            question_id=question.id
        )
        .exclude(
            section=section,
            display_order=display_order
        )
        .exists()
    )

    if already_used:

        return JsonResponse({
            "success": False,
            "message":
                "This question is already used elsewhere in the paper."
        }, status=400)

    # =========================================================
    # CREATE / UPDATE ASSIGNMENT
    # =========================================================

    GeneratedQuestion.objects.update_or_create(

        paper=paper,

        section=section,

        display_order=display_order,

        defaults={
            "question": question,
            "is_manual_replacement": True,
        }
    )

    # =========================================================
    # SUCCESS
    # =========================================================

    return JsonResponse({

        "success": True,

        "message":
            "Question replaced successfully.",

        "question": {

            "id":
                question.id,

            "question_text":
                question.question_text,

            "unit":
                question.unit,

            "marks":
                question.marks,

            "difficulty":
                question.difficulty,

            "bloom_level":
                question.bloom_level,

            "question_type":
                question.question_type,
        }

    })


# =========================================================
# GENERATE PAPER
# =========================================================

@login_required
def generate_paper(
    request,
    pattern_id
):

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    if request.method == "POST":

        generator = PaperGeneratorService(
            pattern,
            request.user
        )

        validation = (
            generator.validate_question_bank()
        )

        if not validation[
            "sufficient_questions"
        ]:

            messages.error(
                request,
                (
                    "Insufficient questions. "
                    f"Required: "
                    f"{validation['details']['total_required']}, "
                    f"Available: "
                    f"{validation['details']['total_available']}"
                )
            )

            return redirect(
                "papers:pattern_list"
            )

        try:

            section_a, section_b, section_c = (
                generator.generate_paper()
            )

            paper = GeneratedPaper.objects.create(

                teacher=request.user,

                pattern=pattern,

                title=(
                    f"{pattern.subject} "
                    f"Question Paper - "
                    f"{timezone.now().strftime('%Y-%m-%d')}"
                ),

                subject=pattern.subject,

                maximum_marks=pattern.total_marks
            )

            paper.section_a_questions.set(
                section_a
            )

            paper.section_b_questions.set(
                section_b
            )

            paper.section_c_questions.set(
                section_c
            )

            # -------------------------------------------------
            # FILE GENERATION
            # -------------------------------------------------

            from apps.formatter.pdf_generator import (
                PDFGenerator
            )

            from apps.formatter.docx_generator import (
                DocxGenerator
            )

            pdf_path = (
                PDFGenerator.generate_paper(
                    paper
                )
            )

            docx_path = (
                DocxGenerator.generate_paper(
                    paper
                )
            )

            paper.pdf_file.name = pdf_path

            paper.docx_file.name = docx_path

            paper.save()

            messages.success(
                request,
                "Paper generated successfully!"
            )

            return redirect(
                "papers:paper_preview_pattern",
                paper_id=paper.id
            )

        except Exception as error:

            messages.error(
                request,
                f"Error generating paper: {str(error)}"
            )

            return redirect(
                "papers:pattern_list"
            )

    return render(
        request,
        "papers/generate_paper.html",
        {
            "pattern":
                pattern
        }
    )


# =========================================================
# PAPER QUALITY CHECK
# =========================================================

@login_required
@require_POST
def paper_quality_api(request):

    from .models import PaperPattern, GeneratedPaper

    # --------------------------------------------------------
    # Read JSON request
    # --------------------------------------------------------

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({
            "success": False,
            "message": "Invalid JSON request."
        }, status=400)

    # --------------------------------------------------------
    # Get pattern ID
    # --------------------------------------------------------

    pattern_id = data.get("pattern_id")

    if not pattern_id:
        return JsonResponse({
            "success": False,
            "message": "Pattern ID is required."
        }, status=400)

    try:
        pattern_id = int(pattern_id)
    except (ValueError, TypeError):
        return JsonResponse({
            "success": False,
            "message": "Invalid pattern ID."
        }, status=400)

    # --------------------------------------------------------
    # Verify pattern belongs to logged-in teacher
    # --------------------------------------------------------

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    # --------------------------------------------------------
    # Find generated paper
    # --------------------------------------------------------

    paper = (
        GeneratedPaper.objects
        .filter(
            pattern=pattern,
            teacher=request.user
        )
        .first()
    )

    if not paper:
        return JsonResponse({
            "success": False,
            "message": "No generated paper was found for this pattern."
        }, status=404)

    # --------------------------------------------------------
    # Run quality checker
    # --------------------------------------------------------

    try:

        result = check_paper_quality(
            paper
        )

        return JsonResponse(
            result,
            status=200
        )

    except Exception as exc:

        return JsonResponse({
            "success": False,
            "message": (
                "Unable to analyze the paper."
            ),
            "error": str(exc),
        }, status=500)






# =========================================================
# DOWNLOAD PAPER
# =========================================================

@login_required
def download_paper(
    request,
    paper_id,
    format_type
):

    paper = get_object_or_404(
        GeneratedPaper,
        id=paper_id,
        teacher=request.user
    )

    if (
        format_type == "pdf"
        and paper.pdf_file
    ):

        response = HttpResponse(
            paper.pdf_file.read(),
            content_type="application/pdf"
        )

        response[
            "Content-Disposition"
        ] = (
            f'attachment; '
            f'filename="{paper.title}.pdf"'
        )

        return response

    elif (
        format_type == "docx"
        and paper.docx_file
    ):

        response = HttpResponse(

            paper.docx_file.read(),

            content_type=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )
        )

        response[
            "Content-Disposition"
        ] = (
            f'attachment; '
            f'filename="{paper.title}.docx"'
        )

        return response

    messages.error(
        request,
        "File not available for download."
    )

    return redirect(
        "papers:paper_preview_pattern",
        paper_id=paper.id
    )


# =========================================================
# GENERATED PAPERS LIST
# =========================================================

@login_required
def generated_papers_list(
    request
):

    papers = (
        GeneratedPaper.objects
        .filter(
            teacher=request.user
        )
        .order_by("-id")
    )

    return render(
        request,
        "papers/generated_papers.html",
        {
            "papers":
                papers
        }
    )


# =========================================================
# API - PATTERN LIST
# =========================================================

@api_view(
    ["GET", "POST"]
)
@login_required
def pattern_api_list(
    request
):

    if request.method == "GET":

        patterns = (
            PaperPattern.objects
            .filter(
                teacher=request.user
            )
        )

        serializer = (
            PaperPatternSerializer(
                patterns,
                many=True
            )
        )

        return Response(
            serializer.data
        )

    serializer = (
        PaperPatternSerializer(
            data=request.data
        )
    )

    if serializer.is_valid():

        serializer.save(
            teacher=request.user
        )

        return Response(
            serializer.data,
            status=201
        )

    return Response(
        serializer.errors,
        status=400
    )


# =========================================================
# API - GENERATE PAPER
# =========================================================

@api_view(
    ["POST"]
)
@login_required
def generate_paper_api(
    request
):

    pattern_id = request.data.get(
        "pattern_id"
    )

    if not pattern_id:

        return Response(
            {
                "error":
                    "pattern_id is required"
            },
            status=400
        )

    try:

        pattern = (
            PaperPattern.objects.get(
                id=pattern_id,
                teacher=request.user
            )
        )

    except PaperPattern.DoesNotExist:

        return Response(
            {
                "error":
                    "Pattern not found"
            },
            status=404
        )

    generator = (
        PaperGeneratorService(
            pattern,
            request.user
        )
    )

    validation = (
        generator.validate_question_bank()
    )

    if not validation[
        "sufficient_questions"
    ]:

        return Response(
            {
                "error":
                    "Insufficient questions",

                "details":
                    validation["details"],
            },
            status=400
        )

    try:

        section_a, section_b, section_c = (
            generator.generate_paper()
        )

        paper = GeneratedPaper.objects.create(

            teacher=request.user,

            pattern=pattern,

            title=(
                f"{pattern.subject} Paper - API"
            ),

            subject=pattern.subject,

            maximum_marks=pattern.total_marks
        )

        paper.section_a_questions.set(
            section_a
        )

        paper.section_b_questions.set(
            section_b
        )

        paper.section_c_questions.set(
            section_c
        )

        serializer = (
            GeneratedPaperSerializer(
                paper
            )
        )

        return Response(
            serializer.data,
            status=201
        )

    except Exception as error:

        return Response(
            {
                "error":
                    str(error)
            },
            status=500
        )


# =========================================================
# API - GENERATED PAPERS
# =========================================================

@api_view(
    ["GET"]
)
@login_required
def generated_papers_api(
    request
):

    papers = (
        GeneratedPaper.objects
        .filter(
            teacher=request.user
        )
    )

    serializer = (
        GeneratedPaperSerializer(
            papers,
            many=True
        )
    )

    return Response(
        serializer.data
    )