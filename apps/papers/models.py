from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from academic.models import Program, Semester, Subject
from apps.questions.models import Question
exam_date = models.DateField(default=timezone.now)
exam_time = models.TimeField(default="10:00")
Teacher = get_user_model()


# ==========================================
# PAPER PATTERN
# ==========================================

class PaperPattern(models.Model):

    EXAM_TYPE_CHOICES = [
        ("regular", "Regular End Semester"),
        ("midterm", "Mid Semester"),
        ("internal", "Internal Assessment"),
        ("practical", "Practical"),
        ("custom", "Custom"),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="paper_patterns"
    )

    program = models.ForeignKey(
    Program,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
)

    semester = models.ForeignKey(
    Semester,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
)

    subject = models.ForeignKey(
    Subject,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
)

    pattern_name = models.CharField(
        max_length=200
    )

    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPE_CHOICES,
        default="regular"
    )

    exam_date = models.DateField()

    time_allowed = models.CharField(
        max_length=50,
        default="1 Hour"
    )

    total_marks = models.PositiveIntegerField()

    paper_header = models.TextField(
        blank=True
    )

    instructions = models.TextField(
        blank=True
    )

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
        ordering = ["-created_at"]

    def __str__(self):
        return self.pattern_name


# ==========================================
# PATTERN ROW
# ==========================================

class PatternSection(models.Model):

    ATTEMPT_CHOICES = [
        ("select attempt rule ", "Select Attempt Rule"),
        ("1of2", "Attempt Any 1 out of 2"),
        ("2of3", "Attempt Any 2 out of 3"),
        ("3of4", "Attempt Any 3 out of 4"),
        ("4of5", "Attempt Any 4 out of 5"),
        ("5of5", "Attempt every question"),
        ("custom", "Custom"),
    ]

    pattern = models.ForeignKey(
        PaperPattern,
        on_delete=models.CASCADE,
        related_name="sections"
    )

    display_order = models.PositiveIntegerField()

    question_number = models.CharField(
        max_length=20
    )

    attempt_rule = models.CharField(
        max_length=20,
        choices=ATTEMPT_CHOICES,
        default="select attempt rule "
    )

    custom_attempt_text = models.CharField(
        max_length=200,
        blank=True
    )

    QUESTION_TYPE_CHOICES = [
        ("mcq", "Multiple choice questions"),
        ("ftq", "Following the questions"),
        ("cs", "Case Study"),
    ]

    unit = models.CharField(
        max_length=10,
        blank=True,
        default=""
    )

    bloom_level = models.CharField(
        max_length=30
    )
    co = models.CharField(
    max_length=10,
    default="CO1"
    )

    difficulty = models.CharField(
        max_length=20
    )

    question_type = models.CharField(
        max_length=30,
        choices=QUESTION_TYPE_CHOICES,
        default="mcq"
    )

    marks = models.PositiveIntegerField()

    number_of_questions = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        ordering = ["display_order"]

    def get_question_type_display_name(self):
        val = (self.question_type or "").lower()
        if val in ["mcq", "multiple choice questions"]:
            return "Multiple choice questions"
        elif val in ["ftq", "following the questions"]:
            return "Following the questions"
        elif val in ["cs", "case study"]:
            return "Case Study"
        return self.get_question_type_display() if hasattr(self, "get_question_type_display") else self.question_type

    def __str__(self):
        return f"{self.pattern.pattern_name} - {self.question_number}"


# ==========================================
# PATTERN QUESTION SETTINGS
# ==========================================

# ==========================================
# PATTERN QUESTION SETTINGS
# ==========================================

class PatternQuestionSetting(models.Model):
    section = models.ForeignKey(
        PatternSection,
        on_delete=models.CASCADE,
        related_name="question_settings"
    )

    slot_number = models.PositiveIntegerField()

    unit = models.CharField(
        max_length=10,
        blank=True,
        default=""
    )

    bloom_level = models.CharField(
        max_length=30,
        default="1"
    )

    co = models.CharField(
        max_length=10,
        default="CO1"
    )

    difficulty = models.CharField(
        max_length=20,
        default="Easy"
    )

    class Meta:
        ordering = ["slot_number"]

        constraints = [
            models.UniqueConstraint(
                fields=["section", "slot_number"],
                name="unique_section_slot"
            )
        ]

    def __str__(self):
        return (
            f"{self.section.question_number} "
            f"- Question {self.slot_number}"
        )


# ==========================================
# GENERATED PAPER
# ==========================================

class GeneratedPaper(models.Model):

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="generated_papers"
    )

    pattern = models.ForeignKey(
        PaperPattern,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    pdf_file = models.FileField(
        upload_to="generated_papers/pdf/",
        blank=True,
        null=True
    )

    docx_file = models.FileField(
        upload_to="generated_papers/docx/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# ==========================================
# GENERATED QUESTIONS
# ==========================================

class GeneratedQuestion(models.Model):

    paper = models.ForeignKey(
        GeneratedPaper,
        on_delete=models.CASCADE,
        related_name="generated_questions"
    )

    section = models.ForeignKey(
        PatternSection,
        on_delete=models.CASCADE
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    display_order = models.PositiveIntegerField()

    class Meta:
        ordering = ["display_order"]