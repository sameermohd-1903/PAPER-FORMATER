from django.urls import path
from . import views

app_name = "academic"

urlpatterns = [

    path(
        '',
        views.principal_dashboard,
        name='dashboard'
    ),

    path(
        'program/add/',
        views.add_program,
        name='add_program'
    ),
    
    path(
    "program/update/",
    views.update_program,
    name="update_program",
    ),
    
    path(
    "program/delete/",
    views.delete_program,
    name="delete_program",
    ),



    path(
        'subject/add/',
        views.add_subject,
        name='add_subject'
    ),
    path(
    'subject/edit/<int:id>/',
    views.edit_subject,
    name='edit_subject'
    ),

    path(
    "subject/delete/",
    views.delete_subject_ajax,
    name="delete_subject_ajax",
),
    
    
    path(
    "subject/update/",
    views.update_subject_ajax,
    name="update_subject_ajax",
),
    
    path(
    'ajax/programs/',
    views.get_programs,
    name='get_programs'
    ),

    path(
    'ajax/semesters/',
    views.get_semesters,
    name='get_semesters'
),
    path(
    'ajax/subjects/',
    views.get_subjects,
    name='get_subjects'
),

]