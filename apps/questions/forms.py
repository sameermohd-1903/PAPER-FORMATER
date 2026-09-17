from django import forms

from academic.models import (
    Program,
    Semester,
    Subject
)

from .models import Question


class SelectionForm(forms.Form):

    level = forms.ChoiceField(
        choices=Program.LEVEL_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        )
    )

    program = forms.ModelChoiceField(
        queryset=Program.objects.none(),
        empty_label="Select Program",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        )
    )

    semester = forms.ModelChoiceField(
        queryset=Semester.objects.none(),
        empty_label="Select Semester",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        )
    )

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        empty_label="Select Subject",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        )
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["program"].queryset = Program.objects.none()
        self.fields["semester"].queryset = Semester.objects.none()
        self.fields["subject"].queryset = Subject.objects.none()


class ExcelUploadForm(forms.Form):

    excel_file = forms.FileField(
        label="Upload Excel File"
    )


class QuestionForm(forms.ModelForm):

    # =========================================================
    # LEVEL
    # =========================================================

    level = forms.ChoiceField(
        choices=Program.LEVEL_CHOICES,
        label="Level",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_level",
            }
        )
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

            # =================================================
            # PROGRAM
            # =================================================

            "program": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_program",
                }
            ),

            # =================================================
            # SEMESTER
            # =================================================

            "semester": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_semester",
                }
            ),

            # =================================================
            # SUBJECT
            # =================================================

            "subject": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_subject",
                }
            ),

            # =================================================
            # UNIT
            # =================================================

            "unit": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            # =================================================
            # QUESTION TYPE
            # =================================================

            "question_type": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_question_type",
                }
            ),

            # =================================================
            # DIFFICULTY
            # =================================================

            "difficulty": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_difficulty",
                }
            ),

            # =================================================
            # BLOOM LEVEL
            # =================================================

            "bloom_level": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_bloom_level",
                }
            ),

            # =================================================
            # MARKS
            # =================================================

            "marks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "Enter marks",
                }
            ),

            # =================================================
            # QUESTION TEXT
            # =================================================

            "question_text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Enter question here...",
                }
            ),
        }

    # =========================================================
    # INITIALIZE FORM
    # =========================================================

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # =====================================================
        # PROGRAM
        # =====================================================

        self.fields["program"].queryset = Program.objects.none()
        self.fields["program"].empty_label = "Select Program"

        # =====================================================
        # SEMESTER
        # =====================================================

        self.fields["semester"].queryset = Semester.objects.none()
        self.fields["semester"].empty_label = "Select Semester"

        # =====================================================
        # SUBJECT
        # =====================================================

        self.fields["subject"].queryset = Subject.objects.none()
        self.fields["subject"].empty_label = "Select Subject"

        # =====================================================
        # WHEN FORM IS SUBMITTED
        # =====================================================

        if self.is_bound:

            level = self.data.get("level")
            program_id = self.data.get("program")
            semester_id = self.data.get("semester")

            # -------------------------------------------------
            # LEVEL → PROGRAM
            # -------------------------------------------------

            if level:

                self.fields["program"].queryset = (
                    Program.objects
                    .filter(level=level)
                    .order_by("name")
                )

            # -------------------------------------------------
            # PROGRAM → SEMESTER
            # -------------------------------------------------

            if program_id:

                self.fields["semester"].queryset = (
                    Semester.objects
                    .filter(
                        program_id=program_id
                    )
                    .order_by("number")
                )

            # -------------------------------------------------
            # SEMESTER → SUBJECT
            # -------------------------------------------------

            if semester_id and program_id:

                self.fields["subject"].queryset = (
                    Subject.objects
                    .filter(
                        semester_id=semester_id,
                        program_id=program_id
                    )
                    .order_by("name")
                )