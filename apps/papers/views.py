from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PaperPattern, GeneratedPaper
from .forms import PaperPatternForm
from .services import PaperGeneratorService
from .serializers import PaperPatternSerializer, GeneratedPaperSerializer
import os
from django.conf import settings
from django.http import HttpResponse
import json
from .models import PatternSection
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import PatternSection
import json
from django.db import transaction
from .models import (PaperPattern,PatternSection,GeneratedPaper,GeneratedQuestion,)
def home(request):
    return HttpResponse("Paper Formatter Home Page")
@login_required
def pattern_list(request):
    patterns = PaperPattern.objects.filter(teacher=request.user)
    return render(request, 'papers/pattern_list.html', {'patterns': patterns})

@login_required
def pattern_builder(request, pattern_id):

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    context = {

        "pattern": pattern,

    }

    return render(
        request,
        "papers/pattern_builder.html",
        context
    )


@login_required
def create_pattern(request):

    if request.method == "POST":

        form = PaperPatternForm(request.POST)

        if form.is_valid():

            pattern = form.save(commit=False)

            pattern.teacher = request.user

            pattern.save()

            messages.success(
                request,
                "Pattern created successfully."
            )

            return redirect("papers:pattern_list")

    else:

        form = PaperPatternForm()

    return render(

        request,

        "papers/create_pattern.html",

        {

            "form": form

        }

    )
    
    
@require_POST
@login_required
def save_pattern_rows(request, pattern_id):

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    data = json.loads(request.body)
    print("=" * 50)
    print(data)
    print("=" * 50)
    rows = data.get("rows", [])

    print(rows)

    print("Received JSON:", data)

    rows = data.get("rows", [])

    print("Rows Received:", len(rows))

    # Delete old rows
    pattern.sections.all().delete()

    # Save new rows
    for row in rows:

        print("Saving:", row)

        PatternSection.objects.create(

            pattern=pattern,

            display_order=row["display_order"],

            question_number=row["question_number"],

            attempt_rule=row["attempt_rule"],

            custom_attempt_text=row.get(
                "custom_attempt_text",
                ""
            ),

            unit=row["unit"],

            bloom_level=row["bloom_level"],

            difficulty=row["difficulty"],

            question_type=row["question_type"],

            marks=row["marks"],

            number_of_questions=row["number_of_questions"],

        )

    print("Saved Successfully!")

    return JsonResponse({

        "success": True,

        "message": "Pattern saved successfully."

    }) 
    
    

@login_required
def get_pattern_rows(request, pattern_id):

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    rows = []

    for row in pattern.sections.all():

        rows.append({

            "id": row.id,

            "display_order": row.display_order,

            "question_number": row.question_number,

            "attempt_rule": row.attempt_rule,

            "unit": row.unit,

            "bloom_level": row.bloom_level,

            "difficulty": row.difficulty,

            "question_type": row.question_type,

            "marks": row.marks,

            "number_of_questions": row.number_of_questions,

        })

    return JsonResponse({

        "rows": rows

    })    
    
@login_required
def save_pattern_builder(request, pattern_id):

    if request.method != "POST":
        return JsonResponse(
            {"success": False},
            status=400
        )

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    data = json.loads(request.body)

    rows = data.get("rows", [])

    # Remove old rows
    PatternSection.objects.filter(
        pattern=pattern
    ).delete()

    for row in rows:

        PatternSection.objects.create(

            pattern=pattern,

            display_order=row["order"],

            question_number=row["question_no"],

            attempt_rule=row["attempt_rule"],

            unit=row["unit"],

            bloom_level=row["bloom"],

            difficulty=row["difficulty"],

            question_type=row["type"],

            marks=row["marks"],

            number_of_questions=row["questions"],

        )

    return JsonResponse({
        "success": True
    })  
    
@login_required
def load_pattern_rows(request, pattern_id):

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    rows = []

    for row in pattern.sections.all():

        rows.append({

            "display_order": row.display_order,

            "question_number": row.question_number,

            "attempt_rule": row.attempt_rule,

            "custom_attempt_text": row.custom_attempt_text,

            "unit": row.unit,

            "bloom_level": row.bloom_level,

            "difficulty": row.difficulty,

            "question_type": row.question_type,

            "marks": row.marks,

            "number_of_questions": row.number_of_questions,

        })

    return JsonResponse({

        "rows": rows

    })    
    
    
@login_required
@require_POST
@transaction.atomic
def save_pattern_rows(request, pattern_id):

    pattern = get_object_or_404(
        PaperPattern,
        id=pattern_id,
        teacher=request.user
    )

    data = json.loads(request.body)

    rows = data.get("rows", [])

    # -------------------------------------
    # Remove old rows
    # -------------------------------------

    pattern.sections.all().delete()

    # -------------------------------------
    # Save new rows
    # -------------------------------------

    for row in rows:

        PatternSection.objects.create(

            pattern=pattern,

            display_order=row["display_order"],

            question_number=row["question_number"],

            attempt_rule=row["attempt_rule"],

            custom_attempt_text=row.get(
                "custom_attempt_text",
                ""
            ),

            unit=row["unit"],

            bloom_level=row["bloom_level"],

            difficulty=row["difficulty"],

            question_type=row["question_type"],

            marks=row["marks"],

            number_of_questions=row["number_of_questions"],

        )

    return JsonResponse({

        "success": True,

        "message": "Pattern Saved Successfully"

    })




@login_required
def generate_paper(request, pattern_id):
    pattern = get_object_or_404(PaperPattern, id=pattern_id, teacher=request.user)
    
    if request.method == 'POST':
        # Validate question bank
        generator = PaperGeneratorService(pattern, request.user)
        validation = generator.validate_question_bank()
        
        if not validation['sufficient_questions']:
            messages.error(request, 
                         f"Insufficient questions. Required: {validation['details']['total_required']}, "
                         f"Available: {validation['details']['total_available']}")
            return redirect('papers:pattern_list')
        
        try:
            # Generate questions
            section_a, section_b, section_c = generator.generate_paper()
            
            # Create paper record
            paper = GeneratedPaper.objects.create(
                teacher=request.user,
                pattern=pattern,
                title=f"{pattern.subject} Question Paper - {timezone.now().strftime('%Y-%m-%d')}",
                subject=pattern.subject,
                maximum_marks=pattern.total_marks
            )
            
            # Add questions to sections
            paper.section_a_questions.set(section_a)
            paper.section_b_questions.set(section_b)
            paper.section_c_questions.set(section_c)
            
            # Generate files
            from apps.formatter.pdf_generator import PDFGenerator
            from apps.formatter.docx_generator import DocxGenerator
            
            pdf_path = PDFGenerator.generate_paper(paper)
            docx_path = DocxGenerator.generate_paper(paper)
            
            paper.pdf_file.name = pdf_path
            paper.docx_file.name = docx_path
            paper.save()
            
            messages.success(request, 'Paper generated successfully!')
            return redirect('papers:paper_preview', paper_id=paper.id)
            
        except Exception as e:
            messages.error(request, f"Error generating paper: {str(e)}")
            return redirect('papers:pattern_list')
    
    return render(request, 'papers/generate_paper.html', {'pattern': pattern})
@login_required
def paper_preview(request, paper_id):
    paper = get_object_or_404(GeneratedPaper, id=paper_id, teacher=request.user)
    return render(request, 'papers/paper_preview.html', {'paper': paper})
@login_required
def download_paper(request, paper_id, format_type):
    paper = get_object_or_404(GeneratedPaper, id=paper_id, teacher=request.user)
    
    if format_type == 'pdf' and paper.pdf_file:
        response = HttpResponse(paper.pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{paper.title}.pdf"'
        return response
    
    elif format_type == 'docx' and paper.docx_file:
        response = HttpResponse(paper.docx_file.read(), 
                              content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{paper.title}.docx"'
        return response
    
    else:
        messages.error(request, 'File not available for download')
        return redirect('papers:paper_preview', paper_id=paper.id)
@login_required
def generated_papers_list(request):
    papers = GeneratedPaper.objects.filter(teacher=request.user)
    return render(request, 'papers/generated_papers.html', {'papers': papers})
# API Views
@api_view(['GET', 'POST'])
@login_required
def pattern_api_list(request):
    if request.method == 'GET':
        patterns = PaperPattern.objects.filter(teacher=request.user)
        serializer = PaperPatternSerializer(patterns, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PaperPatternSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
@api_view(['POST'])
@login_required
def generate_paper_api(request):
    pattern_id = request.data.get('pattern_id')
    if not pattern_id:
        return Response({'error': 'pattern_id is required'}, status=400)
    
    try:
        pattern = PaperPattern.objects.get(id=pattern_id, teacher=request.user)
    except PaperPattern.DoesNotExist:
        return Response({'error': 'Pattern not found'}, status=404)
    
    generator = PaperGeneratorService(pattern, request.user)
    validation = generator.validate_question_bank()
    
    if not validation['sufficient_questions']:
        return Response({
            'error': 'Insufficient questions',
            'details': validation['details']
        }, status=400)
    
    try:
        section_a, section_b, section_c = generator.generate_paper()
        
        paper = GeneratedPaper.objects.create(
            teacher=request.user,
            pattern=pattern,
            title=f"{pattern.subject} Paper - API",
            subject=pattern.subject,
            maximum_marks=pattern.total_marks
        )
        
        paper.section_a_questions.set(section_a)
        paper.section_b_questions.set(section_b)
        paper.section_c_questions.set(section_c)
        
        serializer = GeneratedPaperSerializer(paper)
        return Response(serializer.data, status=201)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)
@api_view(['GET'])
@login_required
def generated_papers_api(request):
    papers = GeneratedPaper.objects.filter(teacher=request.user)
    serializer = GeneratedPaperSerializer(papers, many=True)
    return Response(serializer.data)