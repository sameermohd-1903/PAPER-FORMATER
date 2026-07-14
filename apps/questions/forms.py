from django import forms

from academic.models import (
    Program,
    Semester,
    Subject
)


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

        self.fields[
            'program'
        ].queryset = Program.objects.all()

        self.fields[
            'semester'
        ].queryset = Semester.objects.none()

        self.fields[
            'subject'
        ].queryset = Subject.objects.none()


class ExcelUploadForm(forms.Form):

    excel_file = forms.FileField(
        label='Upload Excel File'
    )