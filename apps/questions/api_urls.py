from django.urls import path
from . import views

urlpatterns = [
    path(
        "question/update/",
        views.update_question_ajax,
        name="update_question_ajax",
    ),
    path(
        "question/delete/",
        views.delete_question_ajax,
        name="delete_question_ajax",
    ),
]