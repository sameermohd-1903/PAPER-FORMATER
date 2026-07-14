class ExcelUploadForm(forms.Form):
    
    excel_file = forms.FileField()

    program_name = forms.CharField(widget=forms.HiddenInput())

    semester = forms.CharField(widget=forms.HiddenInput())

    subject = forms.CharField(widget=forms.HiddenInput())