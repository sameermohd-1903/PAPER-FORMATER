from django import forms
from .models import PaperPattern
from academic.models import Program, Semester, Subject

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

            # "paper_header": forms.Textarea(attrs={
            #     "class": "form-control",
            #     "rows": 3
            # }),

            # "instructions": forms.Textarea(attrs={
            #     "class": "form-control",
            #     "rows": 4
            # }),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # -----------------------------------------
        # PROGRAM
        # -----------------------------------------
        self.fields["program"].queryset = Program.objects.all()

        # -----------------------------------------
        # SEMESTER
        # -----------------------------------------
        self.fields["semester"].queryset = Semester.objects.none()

        # -----------------------------------------
        # SUBJECT
        # -----------------------------------------
        self.fields["subject"].queryset = Subject.objects.none()

        # -----------------------------------------
        # When form is submitted
        # -----------------------------------------
        if self.is_bound:

            program_id = self.data.get("program")

            semester_id = self.data.get("semester")

            # Load only semesters belonging
            # to selected program
            if program_id:

                self.fields["semester"].queryset = Semester.objects.filter(
                    program_id=program_id
                ).order_by("number")

            # Load only subjects belonging
            # to selected semester
            if semester_id and program_id:

                self.fields["subject"].queryset = Subject.objects.filter(
                    semester_id=semester_id,
                    program_id=program_id
                ).order_by("name")