from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db import transaction
from django.views.decorators.http import require_POST

from rest_framework.decorators import api_view
from rest_framework.response import Response

import json

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
        #
        # Example:
        #
        # 2 out of 3 × 5 marks = 10
        # Every question × 5 marks = 5
        #
        # Total = 15
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

        # DO NOT calculate another total here.
        # Keep the teacher-entered total.

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

                PatternQuestionSetting.objects.create(

                    section=section,

                    slot_number=slot_number,

                    bloom_level=str(
                        setting.get(
                            "bloom_level",
                            "1"
                        )
                    ),

                    co=setting.get(
                        "co",
                        "CO1"
                    ),

                    difficulty=setting.get(
                        "difficulty",
                        "Easy"
                    ),
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
    
    import random

    from apps.questions.models import Question

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
        # Make sure settings exist
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

            marks = section.marks

            # =================================================
            # BASE ELIGIBILITY
            #
            # HARD RULES:
            #   SAME TEACHER
            #   SAME PROGRAM
            #   SAME SEMESTER
            #   SAME SUBJECT
            #   SAME MARKS
            #   SAME DIFFICULTY
            #   SAME UNIT (when selected)
            # =================================================

            queryset = Question.objects.filter(
                teacher=teacher,
                is_active=True,
                program=pattern.program,
                semester=pattern.semester,
                subject=pattern.subject,
                marks=marks,
                difficulty__iexact=difficulty,
            )

            # -------------------------------------------------
            # INDIVIDUAL UNIT
            # -------------------------------------------------

            if unit:

                queryset = queryset.filter(
                    unit__iexact=unit
                )

            # =================================================
            # BUILD USED QUESTION IDS
            # EXCEPT THE CURRENT SLOT
            # =================================================

            used_question_ids = set(
                GeneratedQuestion.objects
                .filter(paper=paper)
                .exclude(
                    pk=existing_gq.pk
                    if existing_gq
                    else None
                )
                .values_list(
                    "question_id",
                    flat=True
                )
            )

            if used_question_ids:

                queryset = queryset.exclude(
                    id__in=used_question_ids
                )

            # =================================================
            # KEEP EXISTING QUESTION IF VALID
            # =================================================

            if existing_gq:

                existing_question = (
                    existing_gq.question
                )

                existing_valid = (

                    existing_question.teacher_id
                    == teacher.id

                    and
                    existing_question.is_active

                    and
                    existing_question.program_id
                    == pattern.program_id

                    and
                    existing_question.semester_id
                    == pattern.semester_id

                    and
                    existing_question.subject_id
                    == pattern.subject_id

                    and
                    existing_question.marks
                    == marks

                    and
                    str(
                        existing_question.difficulty
                    ).lower()
                    == difficulty
                )

                # ---------------------------------------------
                # CHECK UNIT
                # ---------------------------------------------

                if unit:

                    existing_valid = (
                        existing_valid
                        and
                        str(
                            existing_question.unit
                        ).strip().lower()
                        == unit.lower()
                    )

                # ---------------------------------------------
                # EXISTING QUESTION IS VALID
                # ---------------------------------------------

                if existing_valid:

                    continue

                # ---------------------------------------------
                # EXISTING QUESTION IS INVALID
                # ---------------------------------------------

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
            #
            # DO NOT CRASH THE WHOLE PREVIEW.
            # Leave this slot empty so teacher can Replace.
            # =================================================

            if not available_questions:

                continue

            # =================================================
            # RANDOM SELECTION
            # =================================================

            selected_question = random.choice(
                available_questions
            )

            # =================================================
            # CREATE GENERATED QUESTION
            # =================================================

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
    }


# =========================================================
# PAPER PREVIEW
# =========================================================

# =========================================================
# PAPER PREVIEW - PATTERN
# =========================================================

@login_required
def paper_preview_pattern(
    request,
    pattern_id
):
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
def paper_pdf(
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
# SECTION QUESTIONS API
# =========================================================

@login_required
def get_section_questions_api(request, pattern_id, section_id):

    from apps.questions.models import Question

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    section = get_object_or_404(
        PatternSection,
        id=section_id,
        pattern=pattern
    )

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
        .select_related("question", "section")
        .order_by("display_order")
    )

    # All question IDs already used in this paper
    used_question_ids = {
        gq.question_id
        for gq in assigned_gqs
        if gq.question_id
    }

    # Current section assignments
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

    for index in range(section.number_of_questions):

        slot_number = index + 1

        setting = next(
            (
                s for s in settings
                if s.slot_number == slot_number
            ),
            None
        )

        current_question = current_section_gqs.get(
            slot_number
        )

        if setting:

            unit = str(
                getattr(setting, "unit", "") or ""
            ).strip()

            bloom_level = str(
                setting.bloom_level or ""
            ).strip()

            difficulty = str(
                setting.difficulty or ""
            ).strip()

        else:

            unit = ""

            bloom_level = ""

            difficulty = ""

        # =====================================================
        # CANDIDATE QUESTIONS
        # =====================================================

        queryset = Question.objects.filter(
            teacher=request.user,
            is_active=True,
            program=pattern.program,
            semester=pattern.semester,
            subject=pattern.subject,
            marks=section.marks,
            difficulty__iexact=difficulty,
        )

        # -----------------------------------------------------
        # UNIT
        # -----------------------------------------------------

        if unit:
            queryset = queryset.filter(
                unit__iexact=unit
            )

        # -----------------------------------------------------
        # BLOOM
        # -----------------------------------------------------

        if bloom_level:
            queryset = queryset.filter(
                bloom_level__iexact=bloom_level
            )

        # -----------------------------------------------------
        # QUESTION TYPE
        # -----------------------------------------------------

        if section.question_type:
            queryset = queryset.filter(
                question_type__iexact=section.question_type
            )

        # -----------------------------------------------------
        # IMPORTANT:
        # Don't offer questions already used in the paper.
        #
        # BUT allow the current question to remain visible.
        # It will be disabled in the UI.
        # -----------------------------------------------------

        candidate_ids = set(
            queryset.values_list(
                "id",
                flat=True
            )
        )

        # Current question should be included even if it is used
        if current_question:

            candidate_ids.add(
                current_question.id
            )

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
            .order_by("id")
        )

        question_data = []

        for question in all_questions:

            is_current = (
                current_question is not None
                and question.id == current_question.id
            )

            is_used = (
                question.id in used_question_ids
                and not is_current
            )

            question_data.append({
                "id": question.id,
                "question_text": question.question_text,
                "unit": question.unit,
                "marks": question.marks,
                "bloom_level": (
                    question.get_bloom_level_display()
                ),
                "bloom_value": question.bloom_level,
                "difficulty": (
                    question.get_difficulty_display()
                ),
                "question_type": (
                    question.get_question_type_display_name()
                    if hasattr(
                        question,
                        "get_question_type_display_name"
                    )
                    else question.get_question_type_display()
                ),
                "is_current": is_current,
                "is_used": is_used,
            })

        slots.append({
            "slot_index": index,
            "display_order": slot_number,
            "letter": letters[index],
            "question_id": (
                current_question.id
                if current_question
                else None
            ),
            "question_text": (
                current_question.question_text
                if current_question
                else None
            ),
            "unit": unit,
            "bloom_level": bloom_level,
            "difficulty": difficulty,
            "marks": section.marks,
            "question_type": section.question_type,
            "questions": question_data,
        })

    # =========================================================
    # RESPONSE
    # =========================================================

    return JsonResponse({
        "success": True,

        "section": {
            "id": section.id,
            "question_number": section.question_number,
            "marks": section.marks,
            "question_type": section.question_type,
            "number_of_questions": section.number_of_questions,
        },

        "slots": slots,
    })


# =========================================================
# ASSIGN QUESTION
# =========================================================

@require_POST
@login_required
def assign_section_question_api(
    request,
    pattern_id
):

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    try:

        data = json.loads(
            request.body
        )

    except (
        json.JSONDecodeError,
        TypeError
    ):

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid JSON."
            },
            status=400
        )

    section_id = data.get(
        "section_id"
    )

    slot_index = data.get(
        "slot_index",
        0
    )

    question_id = data.get(
        "question_id"
    )

    section = get_object_or_404(
        PatternSection,
        id=section_id,
        pattern=pattern
    )

    paper, _ = GeneratedPaper.objects.get_or_create(

        pattern=pattern,

        teacher=request.user,

        defaults={
            "title":
                f"{pattern.pattern_name} Question Paper"
        }
    )

    display_order = (
        int(slot_index) + 1
    )

    from apps.questions.models import Question

    if question_id:

        question = get_object_or_404(
            Question,
            id=question_id,
            teacher=request.user
        )

        GeneratedQuestion.objects.update_or_create(

            paper=paper,

            section=section,

            display_order=display_order,

            defaults={
                "question":
                    question
            }
        )

    else:

        GeneratedQuestion.objects.filter(

            paper=paper,

            section=section,

            display_order=display_order

        ).delete()

    return JsonResponse(
        {
            "success": True,

            "message":
                "Question updated successfully."
        }
    )


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
                "papers:paper_preview",
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
# PAPER PREVIEW
# =========================================================

@login_required
def paper_preview(
    request,
    paper_id
):

    paper = get_object_or_404(
        GeneratedPaper,
        id=paper_id,
        teacher=request.user
    )

    return render(
        request,
        "papers/paper_preview.html",
        {
            "paper":
                paper
        }
    )


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
        "papers:paper_preview",
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