from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from apps.accounts.utils import create_email_verification
from ..forms import (TeacherRegistrationForm,PrincipalRegistrationForm)
from apps.accounts.email_service import (send_verification_email,)

from ..models import Teacher


class TeacherRegisterView(CreateView):

    model = Teacher

    form_class = TeacherRegistrationForm

    template_name = "registration/teacher_register.html"

    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
    
        response = super().form_valid(form)

        verification = create_email_verification(
        self.object
        )

        send_verification_email(
        self.object,
        verification.token
        )

        messages.success(
        self.request,
        "Registration successful. Please verify your email."
        )

        return response



def principal_register(request):

    if Teacher.objects.filter(role="principal").exists():

        messages.error(
            request,
            "Principal/HOD account already exists."
        )

        return redirect("accounts:login")

    if request.method == "POST":

        form = PrincipalRegistrationForm(request.POST)

        if form.is_valid():

            principal = form.save(commit=False)

            principal.username = form.cleaned_data["email"]

            principal.email = form.cleaned_data["email"]

            principal.role = "principal"

            principal.set_password(
                form.cleaned_data["password1"]
            )
            principal.save()

            verification = create_email_verification(
            principal
            )

            send_verification_email(
            principal,
            verification.token
            )

            messages.success(
                request,
                "Principal/HOD registered successfully."
            )

            return redirect("accounts:login")

    else:

        form = PrincipalRegistrationForm()

    return render(
        request,
        "registration/principal_register.html",
        {
            "form": form
        }
    )