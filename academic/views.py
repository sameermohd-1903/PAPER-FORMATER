from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Program, Semester, Subject
from .forms import ProgramForm, SemesterForm, SubjectForm
from django.http import JsonResponse
from .models import Program, Semester
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def principal_dashboard(request):
    return render(request, 'academic/dashboard.html')

def add_program(request):
    
    if request.method == "POST":

        form = ProgramForm(request.POST)

        if form.is_valid():

            program = form.save()

            if program.level == "UG":

                for i in range(1, 7):

                    Semester.objects.create(
                        program=program,
                        number=i
                    )

            elif program.level == "PG":

                for i in range(1, 5):

                    Semester.objects.create(
                        program=program,
                        number=i
                    )

            messages.success(
                request,
                "Program added successfully."
            )

            return redirect("academic:add_program")

        else:

            print("FORM ERRORS:")
            print(form.errors)

    else:

        form = ProgramForm()

    programs = Program.objects.all()

    return render(
        request,
        "academic/add_program.html",
        {
            "form": form,
            "programs": programs,
        },
    )
    
def update_program(request):
    
    if request.method == "POST":

        program = Program.objects.get(
            id=request.POST.get("id")
        )

        program.level = request.POST.get("level")
        program.name = request.POST.get("name")

        program.save()

        return JsonResponse({

            "success": True,
            "id": program.id,
            "level": program.get_level_display(),
            "name": program.name,

        })

    return JsonResponse({

        "success": False

    })   
    
def delete_program(request):
    
    if request.method == "POST":

        try:

            program = Program.objects.get(
                id=request.POST.get("id")
            )

            program.delete()

            return JsonResponse({

                "success": True,
                "message": "Program deleted successfully."

            })

        except Program.DoesNotExist:

            return JsonResponse({

                "success": False,
                "message": "Program not found."

            })

    return JsonResponse({

        "success": False,
        "message": "Invalid request."

    })     

def add_semester(request):
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Semester added successfully.')
            return redirect('academic:add_semester')
    else:
        form = SemesterForm()
    semesters = Semester.objects.all()
    return render(
        request,
        'academic/add_semester.html',
        {
            'form': form,
            'semesters': semesters
        }
    )

def add_subject(request):
    
    if request.method == 'POST':

        print("POST DATA =", request.POST)

        form = SubjectForm(request.POST)

        print("FORM VALID =", form.is_valid())

        print("FORM ERRORS =", form.errors)

        if form.is_valid():

            subject = form.save()

            print("SUBJECT SAVED =", subject.id)

            messages.success(
                request,
                'Subject added successfully.'
            )

            return redirect(
                'academic:add_subject'
            )

    else:

        form = SubjectForm()

    # rest of your code...

    # FILTERS

    level = request.GET.get('level')
    program = request.GET.get('program')
    semester = request.GET.get('semester')

    subjects = Subject.objects.select_related(
        'program',
        'semester'
    )

    if level:
        subjects = subjects.filter(
            program__level=level
        )

    if program:
        subjects = subjects.filter(
            program_id=program
        )

    if semester:
        subjects = subjects.filter(
            semester__number=semester
        )

    programs = Program.objects.all()

    if level:
        programs = programs.filter(
            level=level
        )

    return render(
        request,
        'academic/add_subject.html',
        {
            'form': form,
            'subjects': subjects,
            'programs': programs,
            'selected_level': level,
            'selected_program': program,
            'selected_semester': semester,
        }
    )
    
def edit_subject(request, id):
    
    subject = Subject.objects.get(id=id)

    if request.method == 'POST':

        subject.program_id = request.POST.get('program')
        subject.semester_id = request.POST.get('semester')
        subject.name = request.POST.get('name')

        subject.save()

        messages.success(
            request,
            'Subject updated successfully.'
        )

        return redirect('academic:add_subject')

    programs = Program.objects.filter(
        level=subject.program.level
    )

    semesters = Semester.objects.filter(
        program=subject.program
    )

    return render(
        request,
        'academic/edit_subject.html',
        {
            'subject': subject,
            'programs': programs,
            'semesters': semesters,
        }
    )   
    
'''def update_subject(request, id):
    
    subject = Subject.objects.get(id=id)

    if request.method == 'POST':

        program_id = request.POST.get('program')
        semester_id = request.POST.get('semester')
        name = request.POST.get('name')

        if program_id:
            subject.program_id = program_id

        if semester_id:
            subject.semester_id = semester_id

        subject.name = name

        subject.save()

        messages.success(
            request,
            'Subject updated successfully.'
        )

    return redirect(
    f"{request.path}?level={subject.program.level}&program={subject.program.id}&semester={subject.semester.number}"
)'''



@require_POST
def update_subject_ajax(request):

    try:

        subject = Subject.objects.get(
            id=request.POST.get("id")
        )

        program = Program.objects.get(
            id=request.POST.get("program")
        )

        semester = Semester.objects.get(
            id=request.POST.get("semester")
        )

        subject.program = program
        subject.semester = semester
        subject.name = request.POST.get("name")

        subject.save()

        return JsonResponse({

            "success": True,

            "id": subject.id,

            "level": program.get_level_display(),

            "program": program.name,

            "semester": semester.number,

            "subject": subject.name,

        })

    except Exception as e:

        return JsonResponse({

            "success": False,

            "message": str(e)

        })



    

'''def delete_subject(request, id):
    
    subject = Subject.objects.get(id=id)

    subject.delete()

    messages.success(
        request,
        'Subject deleted successfully.'
    )

    return redirect(
        'academic:add_subject'
    )'''
    


@require_POST
def delete_subject_ajax(request):

    try:

        subject = Subject.objects.get(
            id=request.POST.get("id")
        )

        subject.delete()

        return JsonResponse({

            "success": True,
            "message": "Subject deleted successfully."

        })

    except Subject.DoesNotExist:

        return JsonResponse({

            "success": False,
            "message": "Subject not found."

        })    
    
def get_programs(request):
    level = request.GET.get('level')

    programs = Program.objects.filter(level=level)

    data = [
        {
            'id': program.id,
            'name': program.name,
        }
        for program in programs
    ]

    return JsonResponse(data, safe=False)

def get_semesters(request):
    
    program_id = request.GET.get('program')

    semesters = Semester.objects.filter(
        program_id=program_id
    ).order_by('number')

    data = [
        {
            'id': semester.id,
            'number': semester.number,
            'name': str(semester),
        }
        for semester in semesters
    ]

    return JsonResponse(data, safe=False)

def get_subjects(request):
    
    program_id = request.GET.get('program')
    semester_id = request.GET.get('semester')

    subjects = Subject.objects.filter(
        program_id=program_id,
        semester_id=semester_id
    )

    data = []

    for subject in subjects:

        data.append({
            'id': subject.id,
            'name': subject.name
        })

    return JsonResponse(data, safe=False)