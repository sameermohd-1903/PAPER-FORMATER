from django.db import models
from django.contrib.auth import get_user_model
from academic.models import Program, Semester, Subject

Teacher = get_user_model()


class Question(models.Model):

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    QUESTION_TYPE_CHOICES = [
        ('mcq', 'MCQ'),
        ('very_short', 'Very Short'),
        ('short', 'Short Answer'),
        ('long', 'Long Answer'),
        ('case_study', 'Case Study'),
        ('programming', 'Programming'),
        ('numerical', 'Numerical'),
    ]

    BLOOM_LEVEL_CHOICES = [
        ('remember', 'Remember'),
        ('understand', 'Understand'),
        ('apply', 'Apply'),
        ('analyze', 'Analyze'),
        ('evaluate', 'Evaluate'),
        ('create', 'Create'),
    ]

    UNIT_CHOICES = [
        ('1', 'Unit 1'),
        ('2', 'Unit 2'),
        ('3', 'Unit 3'),
        ('4', 'Unit 4'),
        ('5', 'Unit 5'),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='questions'
    )

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    unit = models.CharField(
        max_length=2,
        choices=UNIT_CHOICES
    )

    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES
    )

    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES
    )

    bloom_level = models.CharField(
        max_length=20,
        choices=BLOOM_LEVEL_CHOICES
    )

    marks = models.PositiveIntegerField()

    question_text = models.TextField()

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.subject.name} | "
            f"Unit {self.unit} | "
            f"{self.marks} Marks"
        )