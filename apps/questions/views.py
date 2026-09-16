from pathlib import Path
from academic.models import Program, Semester, Subject
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from .excel_import import ExcelImporter
from .forms import ExcelUploadForm, SelectionForm, QuestionForm
from .models import Question
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .ai_service import classify_question
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .question_regeneration_service import (
    generate_valid_unique_question,
)
from .ai_service import classify_question

@login_required
def question_list(request):

    questions = Question.objects.select_related(
        "program",
        "semester",
        "subject"
    ).filter(
        teacher=request.user
    )

    level = request.GET.get("level")
    program = request.GET.get("program")
    semester = request.GET.get("semester")
    subject = request.GET.get("subject")
    unit = request.GET.get("unit")
    question_type = request.GET.get("question_type")
    difficulty = request.GET.get("difficulty")
    bloom = request.GET.get("bloom")
    marks = request.GET.get("marks")

    if level:
        questions = questions.filter(program__level=level)

    if program:
        questions = questions.filter(program_id=program)

    if semester:
        questions = questions.filter(semester_id=semester)

    if subject:
        questions = questions.filter(subject_id=subject)

    if unit:
        questions = questions.filter(unit=unit)

    if question_type:
        questions = questions.filter(question_type=question_type)

    if difficulty:
        questions = questions.filter(difficulty=difficulty)

    if bloom:
        questions = questions.filter(bloom_level=bloom)

    if marks:
        questions = questions.filter(marks=marks)

    paginator = Paginator(
        questions,
        20
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    total_questions = questions.count()

    easy_count = questions.filter(
        difficulty="easy"
    ).count()

    medium_count = questions.filter(
        difficulty="medium"
    ).count()

    hard_count = questions.filter(
        difficulty="hard"
    ).count()

    context = {

        "page_obj": page_obj,

        "programs": Program.objects.all(),

        "semesters": Semester.objects.all(),

        "subjects": Subject.objects.all(),

        "selected_level": level,

        "selected_program": program,

        "selected_semester": semester,

        "selected_subject": subject,

        "selected_unit": unit,

        "selected_type": question_type,

        "selected_difficulty": difficulty,

        "selected_bloom": bloom,

        "selected_marks": marks,

        "total_questions": total_questions,

        "easy_count": easy_count,

        "medium_count": medium_count,

        "hard_count": hard_count,

    }

    return render(
        request,
        "questions/list.html",
        context
    )








@login_required
@require_POST
def classify_question_ajax(request):

    question_text = request.POST.get(
        "question_text",
        ""
    ).strip()

    if not question_text:

        return JsonResponse(
            {
                "success": False,
                "message": "Please enter a question first."
            },
            status=400
        )

    try:

        result = classify_question(
            question_text
        )

        return JsonResponse(
            {
                "success": True,
                "bloom_level": result["bloom_level"],
                "difficulty": result["difficulty"],
                "question_type": result["question_type"],
            }
        )

    except Exception as e:

        return JsonResponse(
            {
                "success": False,
                "message": str(e)
            },
            status=500
        )




@require_POST
@login_required
def check_question_similarity_ajax(request):
    question_text = request.POST.get("question_text", "").strip()
    program_id = request.POST.get("program")
    semester_id = request.POST.get("semester")
    subject_id = request.POST.get("subject")

    if not question_text:
        return JsonResponse({
            "success": False,
            "message": "Question text cannot be empty."
        }, status=400)

    if not program_id or not semester_id or not subject_id:
        return JsonResponse({
            "success": False,
            "message": "Please select Program, Semester and Subject first."
        }, status=400)

    try:
        from .embedding_service import generate_embedding
        from .similarity_service import find_similar_questions

        # Generate embedding for the new question
        new_embedding = generate_embedding(question_text)

        # Compare only with questions from the same
        # program + semester + subject + teacher
        questions = Question.objects.filter(
            teacher=request.user,
            program_id=program_id,
            semester_id=semester_id,
            subject_id=subject_id,
            embedding__isnull=False,
        )

        matches = find_similar_questions(
            new_embedding,
            questions,
            threshold=0.70,
            limit=5,
        )

        return JsonResponse({
            "success": True,
            "has_similar": bool(matches),
            "matches": matches,
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e),
        }, status=500)





@login_required
def select_subject(request):

    if request.method == 'POST':

        request.session['program'] = request.POST.get('program')
        request.session['semester'] = request.POST.get('semester')
        request.session['subject'] = request.POST.get('subject')

        return redirect('questions:upload')

    return render(
        request,
        'questions/select_subject.html'
    )


@login_required
def question_add(request):

    if request.method == "POST":

        form = QuestionForm(request.POST)

        if form.is_valid():

            question = form.save(commit=False)

            # ---------------------------------------------
            # Set logged-in teacher
            # ---------------------------------------------

            question.teacher = request.user

            # ---------------------------------------------
            # Get question text
            # ---------------------------------------------

            question_text = (
                question.question_text or ""
            ).strip()

            if not question_text:

                messages.error(
                    request,
                    "Question text cannot be empty."
                )

                return render(
                    request,
                    "questions/add.html",
                    {"form": form}
                )

            # ---------------------------------------------
            # AI QUESTION CLASSIFICATION
            # ---------------------------------------------

            try:

                ai_result = classify_question(
                    question_text
                )

                question.bloom_level = (
                    ai_result["bloom_level"]
                )

                question.difficulty = (
                    ai_result["difficulty"]
                )

                question.question_type = (
                    ai_result["question_type"]
                )

            except Exception as e:

                messages.error(
                    request,
                    f"AI classification failed: {e}"
                )

                return render(
                    request,
                    "questions/add.html",
                    {"form": form}
                )

            # ---------------------------------------------
            # Generate embedding
            # ---------------------------------------------

            try:

                from .embedding_service import (
                    generate_embedding
                )

                question.embedding = (
                    generate_embedding(
                        question_text
                    )
                )

            except Exception as e:

                messages.error(
                    request,
                    f"Question embedding failed: {e}"
                )

                return render(
                    request,
                    "questions/add.html",
                    {"form": form}
                )

            # ---------------------------------------------
            # Save question
            # ---------------------------------------------

            question.save()

            messages.success(
                request,
                (
                    "Question added successfully. "
                    "Bloom, difficulty and question type "
                    "were classified by AI."
                )
            )

            return redirect(
                "questions:list"
            )

    else:

        form = QuestionForm()

    return render(
        request,
        "questions/add.html",
        {
            "form": form
        }
    )





@login_required
def upload_questions(request):

    program_id = request.session.get('program')
    semester_id = request.session.get('semester')
    subject_id = request.session.get('subject')

    if not all([program_id, semester_id, subject_id]):
        return redirect('questions:select')

    program = Program.objects.get(id=program_id)
    semester = Semester.objects.get(id=semester_id)
    subject = Subject.objects.get(id=subject_id)

    if request.method == 'POST':

        form = ExcelUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            excel_file = request.FILES['excel_file']

            uploads_dir = Path(settings.MEDIA_ROOT) / "uploads"

            uploads_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            file_path = uploads_dir / excel_file.name

            with open(file_path, "wb+") as destination:

                for chunk in excel_file.chunks():
                    destination.write(chunk)

            importer = ExcelImporter(
                str(file_path),
                request.user,
                program,
                semester,
                subject
            )

            success, result = importer.import_data()

            file_path.unlink(missing_ok=True)

            if success:
    
               messages.success(request, result)

               # Remove only these session values
               request.session.pop("program", None)
               request.session.pop("semester", None)
               request.session.pop("subject", None)

               return redirect("questions:list")

                

            for error in result:
                messages.error(request, error)

    else:

        form = ExcelUploadForm()

    return render(
        request,
        'questions/upload.html',
        {
            'form': form,
            'program': program,
            'semester': semester,
            'subject': subject,
        }
    )


@login_required
def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk, teacher=request.user)

    if request.method == 'POST':
        question.program = Program.objects.get(
    id=request.POST.get("program"))

        question.semester = Semester.objects.get(id=request.POST.get("semester"))

        question.subject = Subject.objects.get(id=request.POST.get("subject"))
        question.question_text = request.POST.get('question_text')
        question.bloom_level = request.POST.get('bloom_level')
        question.marks = request.POST.get('marks')
        question.unit = request.POST.get("unit")
        question.question_type = request.POST.get("question_type")

        question.difficulty = request.POST.get("difficulty")
        question.save()

        messages.success(request, 'Question Updated Successfully')
        return redirect('questions:list')

    return render(request, 'questions/edit.html', {'question': question})



from django.shortcuts import render, redirect


def teacher_dashboard(request):

    return render(
        request,
        'teacher/dashboard.html'
    )


def teacher_select(request):

    if request.method == 'POST':

        level = request.POST.get('level')
        program = request.POST.get('program')
        semester = request.POST.get('semester')
        subject = request.POST.get('subject')

        print(level)
        print(program)
        print(semester)
        print(subject)

        return redirect(
            'questions:dashboard'
        )

    return render(
        request,
        'questions/upload.html'
    )
    

@require_POST
@login_required
def delete_question_ajax(request):

    try:

        question = get_object_or_404(
            Question,
            id=request.POST.get("id"),
            teacher=request.user
        )

        question.delete()

        return JsonResponse({

            "success": True,
            "message": "Question deleted successfully."

        })

    except Exception as e:

        return JsonResponse({

            "success": False,
            "message": str(e)

        })



@require_POST
@login_required
def update_question_ajax(request):

    question = get_object_or_404(
        Question,
        id=request.POST.get("id"),
        teacher=request.user
    )

    question.program_id = request.POST.get("program")
    question.semester_id = request.POST.get("semester")
    question.subject_id = request.POST.get("subject")
    question.unit = request.POST.get("unit")
    question.question_type = request.POST.get("question_type")
    question.difficulty = request.POST.get("difficulty")
    question.bloom_level = request.POST.get("bloom_level")
    question.marks = request.POST.get("marks")
    question.question_text = request.POST.get("question_text")

    question.save()

    return JsonResponse({

        "success": True,

        "message": "Question updated successfully.",

        "id": question.id,

        "program": question.program.name,

        "semester": question.semester.number,

        "subject": question.subject.name,

        "unit": question.unit,

        "question_type": question.get_question_type_display(),

        "difficulty": question.get_difficulty_display(),

        "bloom_level": question.get_bloom_level_display(),

        "marks": question.marks,

        "question_text": question.question_text,

    })
    
  