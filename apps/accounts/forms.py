from django import forms
from .models import Teacher


class PrincipalRegistrationForm(forms.ModelForm):

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Password"
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm Password"
        })
    )

    class Meta:
        model = Teacher
        fields = [
            "first_name",
            "email",
            "phone_number",
        ]

        widgets = {

            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Full Name"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email Address"
            }),

            "phone_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone Number"
            }),

        }

    def clean_email(self):

        email = self.cleaned_data["email"]

        if Teacher.objects.filter(email=email).exists():

            raise forms.ValidationError(
                "Email already registered."
            )

        return email

    def clean_phone_number(self):

        phone = self.cleaned_data["phone_number"]

        if Teacher.objects.filter(phone_number=phone).exists():

            raise forms.ValidationError(
                "Phone number already registered."
            )

        return phone

    def clean(self):

        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:

            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data

    def save(self, commit=True):

        user = super().save(commit=False)

        user.username = self.cleaned_data["email"]

        user.role = "principal"

        user.set_password(
            self.cleaned_data["password1"]
        )

        if commit:
            user.save()

        return user


class TeacherRegistrationForm(forms.ModelForm):

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Password"
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm Password"
        })
    )

    class Meta:

        model = Teacher

        fields = [

            "first_name",

            "last_name",

            "email",

            "phone_number",

            "department",

        ]

        widgets = {

            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "First Name"
            }),

            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Last Name"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email Address"
            }),

            "phone_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone Number"
            }),

            "department": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Department"
            }),

        }

    def clean_email(self):

        email = self.cleaned_data["email"]

        if Teacher.objects.filter(email=email).exists():

            raise forms.ValidationError(
                "Email already exists."
            )

        return email

    def clean_phone_number(self):

        phone = self.cleaned_data["phone_number"]

        if Teacher.objects.filter(phone_number=phone).exists():

            raise forms.ValidationError(
                "Phone number already exists."
            )

        return phone

    def clean(self):

        cleaned_data = super().clean()

        if cleaned_data.get("password1") != cleaned_data.get("password2"):

            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data

    def save(self, commit=True):

        user = super().save(commit=False)

        user.username = self.cleaned_data["email"]

        user.role = "teacher"

        user.set_password(
            self.cleaned_data["password1"]
        )

        if commit:
            user.save()

        return user