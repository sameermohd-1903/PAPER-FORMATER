from django.urls import path
from . import views

app_name = "questions"

urlpatterns = [
    path("", views.question_list, name="list"),
    path("select/", views.select_subject, name="select"),
    path('add/', views.question_add, name='add'),
    path("upload/", views.upload_questions, name="upload"),
    path("edit/<int:pk>/", views.edit_question, name="edit"),
    path("ai/classify/",views.classify_question_ajax,name="ai_classify"),
    path("ai/similarity/", views.check_question_similarity_ajax, name="ai_similarity"),
    path("ajax/check-similarity/",views.check_question_similarity_ajax,name="check_similarity_ajax"),
    #path("delete/<int:pk>/", views.delete_question, name="delete"),
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
