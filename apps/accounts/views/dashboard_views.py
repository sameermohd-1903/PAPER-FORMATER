from django.shortcuts import render
from django.contrib.auth.decorators import login_required


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.questions.models import Question
from academic.models import Subject
from apps.papers.models import GeneratedPaper


@login_required
def dashboard(request):

    # Total questions uploaded by this teacher
    total_questions = Question.objects.filter(
        teacher=request.user
    ).count()

    # Total subjects
    total_subjects = Subject.objects.count()

    # Generated papers by this teacher
    generated_papers = GeneratedPaper.objects.filter(
        teacher=request.user
    ).order_by("-created_at")

    context = {
        "total_questions": total_questions,
        "total_subjects": total_subjects,
        "generated_papers": generated_papers.count(),
        "recent_generated_papers": generated_papers[:5],
    }

    return render(
        request,
        "dashboard.html",
        context
    )


@login_required
def principal_dashboard(request):

    return render(
        request,
        "academic/dashboard.html"
    )