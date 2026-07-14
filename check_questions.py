import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.questions.models import Question

qs = Question.objects.filter(subject='DBMS')
print(f"Total DBMS questions: {qs.count()}")
print("\nMark values distribution:")
for q in qs:
    print(f"  Q: {q.question_text[:50]}... | Marks: {q.marks} | Difficulty: {q.difficulty}")
