class SelectionForm(forms.Form):
    
    program_name = forms.ChoiceField(
        choices=PROGRAM_CHOICES
    )

    semester = forms.ChoiceField(
        choices=[
            ('Sem1','Sem1'),
            ('Sem2','Sem2'),
            ('Sem3','Sem3'),
            ('Sem4','Sem4'),
            ('Sem5','Sem5'),
            ('Sem6','Sem6'),
        ]
    )

    subject = forms.CharField()