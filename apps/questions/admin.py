from django.contrib import admin
from .models import Question

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):


    list_display = (
    'program',
    'semester',
    'subject',
    'marks',
    'teacher',
    'created_at'
)

search_fields = (
    'subject',
    'question_text'
)

list_filter = (
    'program_name',
    'semester',
    'subject'
)

