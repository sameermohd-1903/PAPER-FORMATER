from django import forms
from .models import Program, Semester, Subject



class ProgramForm(forms.ModelForm):

    class Meta:
        model = Program
        fields = ['level', 'name']

        widgets = {
            'level': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }


class SemesterForm(forms.ModelForm):

    class Meta:
        model = Semester
        fields = ['program', 'number']


class SubjectForm(forms.ModelForm):

    class Meta:
        model = Subject
        fields = ['program', 'semester', 'name']

        widgets = {
            'program': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'semester': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
        }


