class PrincipalRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput
    )

    class Meta:
        model = Teacher
        fields = ('first_name', 'email')

    def clean(self):
        cleaned_data = super().clean()

        if (
            cleaned_data.get('password1')
            != cleaned_data.get('password2')
        ):
            raise forms.ValidationError(
                "Passwords do not match"
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.role = 'principal'

        user.set_password(
            self.cleaned_data['password1']
        )

        if commit:
            user.save()

        return user