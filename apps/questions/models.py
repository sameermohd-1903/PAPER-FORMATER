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
        ('mcq', 'Multiple choice questions'),
        ('ftq', 'Following the questions'),
        ('cs', 'Case Study'),
    ]
    
    
    BLOOM_LEVEL_CHOICES = [
        ('1', 'Remember'),
        ('2', 'Understand'),
        ('3', 'Apply'),
        ('4', 'Analyze'),
        ('5', 'Evaluate'),
        ('6', 'Create'),
    ]


    BLOOM_ACTION_VERBS = {
    '1': [
        'Choose',
        'Define',
        'Find',
        'Label',
        'List',
        'Match',
        'Name',
        'Recall',
        'Relate',
        'Select',
        'Show',
        'Spell',
        'Tell',
        'What',
        'When',
        'Where',
        'Which',
        'Who',
        'Why',
    ],

    '2': [
        'Classify',
        'Compare',
        'Contrast',
        'Demonstrate',
        'Explain',
        'Extend',
        'Illustrate',
        'Infer',
        'Interpret',
        'Outline',
        'Relate',
        'Rephrase',
        'Show',
        'Summarize',
        'Translate',
    ],

    '3': [
        'Apply',
        'Build',
        'Choose',
        'Construct',
        'Develop',
        'Experiment with',
        'Identify',
        'Interview',
        'Make use of',
        'Model',
        'Organize',
        'Plan',
        'Select',
        'Solve',
        'Utilize',
    ],

    '4': [
        'Analyze',
        'Assume',
        'Categorize',
        'Classify',
        'Compare',
        'Conclusion',
        'Contrast',
        'Discover',
        'Dissect',
        'Distinguish',
        'Divide',
        'Examine',
        'Function',
        'Inference',
        'Inspect',
        'List',
        'Motive',
        'Relationships',
        'Simplify',
        'Survey',
        'Take part in',
        'Test for',
        'Theme',
    ],

    '5': [
        'Agree',
        'Appraise',
        'Assess',
        'Award',
        'Choose',
        'Compare',
        'Conclude',
        'Criticize',
        'Decide',
        'Deduct',
        'Defend',
        'Determine',
        'Disprove',
        'Estimate',
        'Evaluate',
        'Explain',
        'Importance',
        'Influence',
        'Interpret',
        'Judge',
        'Justify',
        'Mark',
        'Measure',
        'Opinion',
        'Perceive',
        'Prioritize',
        'Prove',
        'Rate',
        'Recommend',
        'Rule on',
        'Select',
        'Support',
        'Value',
    ],

    '6': [
        'Adapt',
        'Build',
        'Change',
        'Choose',
        'Combine',
        'Compile',
        'Compose',
        'Construct',
        'Create',
        'Delete',
        'Design',
        'Develop',
        'Discuss',
        'Elaborate',
        'Estimate',
        'Formulate',
        'Happen',
        'Imagine',
        'Improve',
        'Invent',
        'Make up',
        'Maximize',
        'Minimize',
        'Modify',
        'Original',
        'Originate',
        'Plan',
        'Predict',
        'Propose',
        'Solution',
        'Solve',
        'Suppose',
        'Test',
        'Theory',
    ],
}

    UNIT_CHOICES = [
        ('1', 'Unit 1'),
        ('2', 'Unit 2'),
        ('3', 'Unit 3'),
        ('4', 'Unit 4'),
        ('5', 'Unit 5'),
        ('6', 'Unit 6'),
        ('7', 'Unit 7'),
        ('8', 'Unit 8'),
        ('All', 'All Units'),
      
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
        max_length=3,
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
    embedding = models.JSONField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.subject.name} | "
            f"Unit {self.unit} | "
            f"{self.marks} Marks"
        )