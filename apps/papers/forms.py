from django import forms
from .models import PaperPattern


class PaperPatternForm(forms.ModelForm):

    class Meta:

        model = PaperPattern

        fields = [

            "program",
            "semester",
            "subject",
            "pattern_name",
            "exam_type",
            "exam_date",
            "time_allowed",
            "total_marks",
            "paper_header",
            "instructions",

        ]

        widgets = {

            "program": forms.Select(attrs={
                "class": "form-control"
            }),

            "semester": forms.Select(attrs={
                "class": "form-control"
            }),

            "subject": forms.Select(attrs={
                "class": "form-control"
            }),

            "pattern_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "exam_type": forms.Select(attrs={
                "class": "form-control"
            }),

            "exam_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "time_allowed": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "total_marks": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "paper_header": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),

            "instructions": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),

        }