from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password

from apps.accounts.models import PasswordOTP, Teacher
from apps.accounts.utils import create_password_otp
from apps.accounts.email_service import send_password_otp


def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        user_id = request.session.get("reset_user")

        if not user_id:
            messages.error(
                request,
                "Password reset session expired."
            )
            return redirect("accounts:forgot_password")

        try:
            otp_obj = PasswordOTP.objects.get(
                user_id=user_id,
                otp=otp
            )
        except PasswordOTP.DoesNotExist:
            messages.error(
                request,
                "Invalid OTP."
            )
            return redirect("accounts:verify_otp")

        if otp_obj.is_expired():
            otp_obj.delete()
            messages.error(
                request,
                "OTP has expired."
            )
            return redirect("accounts:forgot_password")

        if otp_obj.is_verified:
            messages.error(
                request,
                "OTP has already been used."
            )
            return redirect("accounts:forgot_password")

        if otp_obj.attempts >= 5:
            otp_obj.delete()
            messages.error(
                request,
                "Too many incorrect attempts. Please request a new OTP."
            )
            return redirect("accounts:forgot_password")

        otp_obj.is_verified = True
        otp_obj.save()

        request.session["otp_verified"] = True

        messages.success(
            request,
            "OTP verified successfully."
        )

        return redirect("accounts:reset_password")

    return render(
        request,
        "registration/verify_otp.html"
    )


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        role = request.POST.get("role")

        try:
            user = Teacher.objects.get(
                email=email,
                role=role
            )
        except Teacher.DoesNotExist:
            messages.error(
                request,
                "No account found with this email."
            )
            return redirect("accounts:forgot_password")

        existing = PasswordOTP.objects.filter(
            user=user
        ).first()

        if existing and not existing.is_expired():
            messages.error(
                request,
                "An OTP has already been sent. Please wait before requesting another."
            )
            return redirect("accounts:verify_otp")

        otp = create_password_otp(user)

        send_password_otp(
            user.email,
            otp
        )

        request.session["reset_user"] = user.id

        messages.success(
            request,
            "OTP has been sent to your email."
        )

        return redirect("accounts:verify_otp")

    return render(
        request,
        "registration/forgot_password.html"
    )


def reset_password(request):
    
    if not request.session.get("otp_verified"):

        messages.error(
            request,
            "Verify OTP first."
        )

        return redirect(
            "accounts:forgot_password"
        )

    if request.method == "POST":

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect(
                "accounts:reset_password"
            )

        if len(password1) < 8:

            messages.error(
                request,
                "Password must be at least 8 characters."
            )

            return redirect(
                "accounts:reset_password"
            )

        user = Teacher.objects.get(
            id=request.session["reset_user"]
        )

        user.set_password(password1)
        user.save()

        PasswordOTP.objects.filter(
            user=user
        ).delete()

        request.session.pop("reset_user", None)
        request.session.pop("otp_verified", None)

        messages.success(
            request,
            "Password changed successfully."
        )

        return redirect(
            "accounts:login"
        )

    return render(
        request,
        "registration/reset_password.html"
    )