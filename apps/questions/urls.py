from django.urls import path
from . import views

app_name = "questions"

urlpatterns = [
    path("", views.question_list, name="list"),
    path("select/", views.select_subject, name="select"),
    path("upload/", views.upload_questions, name="upload"),
    path("edit/<int:pk>/", views.edit_question, name="edit"),
    # path("delete/<int:pk>/", views.delete_question, name="delete"),
]







'''
from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [


path(
    '',
    views.question_list,
    name='list'
),

path(
    'select/',
    views.select_subject,
    name='select'
),

path(
    'upload/',
    views.upload_questions,
    name='upload'
),

path(
    'edit/<int:pk>/',
    views.edit_question,
    name='edit'
),

path(
    'delete/<int:pk>/',
    views.delete_question,
    name='delete'
),




]'''
