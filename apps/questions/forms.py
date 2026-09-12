from django import forms

from academic.models import (
    Program,
    Semester,
    Subject
)

from .models import Question


class SelectionForm(forms.Form):

    level = forms.ChoiceField(
        choices=Program.LEVEL_CHOICES
    )

    program = forms.ModelChoiceField(
        queryset=Program.objects.none()
    )

    semester = forms.ModelChoiceField(
        queryset=Semester.objects.none()
    )

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none()
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["program"].queryset = Program.objects.all()

        self.fields["semester"].queryset = Semester.objects.none()

        self.fields["subject"].queryset = Subject.objects.none()


class ExcelUploadForm(forms.Form):

    excel_file = forms.FileField(
        label="Upload Excel File"
    )


class QuestionForm(forms.ModelForm):

    level = forms.ChoiceField(
        choices=Program.LEVEL_CHOICES,
        label="Level"
    )

    class Meta:

        model = Question

        fields = [
            "level",
            "program",
            "semester",
            "subject",
            "unit",
            "question_type",
            "difficulty",
            "bloom_level",
            "marks",
            "question_text",
        ]

        widgets = {

            "program": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_program",
                }
            ),

            "semester": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_semester",
                }
            ),

            "subject": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_subject",
                }
            ),

            "unit": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "question_type": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_question_type",
                }
            ),

            "difficulty": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_difficulty",
                }
            ),

            "bloom_level": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_bloom_level",
                }
            ),

            "marks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "Enter marks",
                }
            ),

            "question_text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Enter question here...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["program"].queryset = Program.objects.all()

        self.fields["semester"].queryset = Semester.objects.none()

        self.fields["subject"].queryset = Subject.objects.none()

        # When the form is submitted
        if self.is_bound:

            program_id = self.data.get("program")
            semester_id = self.data.get("semester")

            if program_id:

                self.fields["semester"].queryset = Semester.objects.filter(
                    program_id=program_id
                ).order_by("number")

            if semester_id:

                self.fields["subject"].queryset = Subject.objects.filter(
                    semester_id=semester_id
                ).order_by("name")