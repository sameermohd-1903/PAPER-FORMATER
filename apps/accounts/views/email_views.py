from django.shortcuts import redirect,render
from django.contrib import messages

from apps.accounts.models import EmailVerification






def verify_email_sent(request):
    
    return render(
        request,
        "registration/verify_email_sent.html"
    )
    
from django.shortcuts import redirect
from django.contrib import messages

from apps.accounts.models import (
    Teacher,
    EmailVerification,
)

from apps.accounts.utils import (
    create_email_verification,
)

from apps.accounts.email_service import (
    send_verification_email,
)


def resend_verification_email(request):

    if request.method != "POST":

        return redirect(
            "accounts:login"
        )

    email = request.POST.get("email")

    try:

        user = Teacher.objects.get(
            email=email
        )

    except Teacher.DoesNotExist:

        messages.error(
            request,
            "No account found."
        )

        return redirect(
            "accounts:login"
        )

    if user.is_email_verified:

        messages.info(
            request,
            "Your email is already verified."
        )

        return redirect(
            "accounts:login"
        )

    EmailVerification.objects.filter(
        user=user
    ).delete()

    verification = create_email_verification(
        user
    )

    send_verification_email(
        user,
        verification.token
    )

    messages.success(
        request,
        "A new verification email has been sent."
    )

    return redirect(
        "accounts:login"
    )    


def verify_email(request, token):

    try:
        verification = EmailVerification.objects.get(
            token=token
        )

    except EmailVerification.DoesNotExist:

        messages.error(
            request,
            "Invalid verification link."
        )

        return redirect("accounts:login")

    if verification.is_verified:

        messages.info(
            request,
            "Email already verified."
        )

        return redirect("accounts:login")

    if verification.is_expired():

        verification.delete()

        messages.error(
            request,
            "Verification link has expired."
        )

        return redirect("accounts:login")

    verification.is_verified = True
    verification.save()

    user = verification.user
    user.is_email_verified = True
    user.save()

    messages.success(
        request,
        "Email verified successfully."
    )

    return redirect("accounts:login")


def verify_email(request, token):

    try:

        verification = EmailVerification.objects.get(
            token=token
        )

    except EmailVerification.DoesNotExist:

        messages.error(
            request,
            "Invalid verification link."
        )

        return redirect("accounts:login")

    if verification.is_verified:

        messages.info(
            request,
            "Email already verified."
        )

        return redirect("accounts:login")

    if verification.is_expired():

        verification.delete()

        messages.error(
            request,
            "Verification link has expired."
        )

        return redirect("accounts:login")

    verification.is_verified = True
    verification.save()

    user = verification.user

    user.is_email_verified = True
    user.save()

    messages.success(
        request,
        "Email verified successfully."
    )

    return redirect("accounts:login")