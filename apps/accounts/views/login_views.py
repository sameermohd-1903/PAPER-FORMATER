from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
)
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.accounts.device_utils import get_device_information
from apps.accounts.email_service import send_device_otp
from apps.accounts.models import TrustedDevice
from apps.accounts.utils import create_device_otp


def teacher_login(request):

    if request.method == "POST":

        username = request.POST.get("username")

        password = request.POST.get("password")

        selected_role = request.POST.get("role")

        user = authenticate(
            username=username,
            password=password
        )

        if not user:

            messages.error(
                request,
                "Invalid Credentials."
            )

            return redirect(
                "accounts:login"
            )

        # ---------------- Role Check ---------------- #

        if user.role != selected_role:

            messages.error(
                request,
                f"This account is not a {selected_role} account."
            )

            return redirect(
                "accounts:login"
            )

        # ---------------- Email Verification ---------------- #

        if not user.is_email_verified:

            messages.error(
                request,
                "Please verify your email before logging in."
            )

            return redirect(
                "accounts:login"
            )

        # ---------------- Device Detection ---------------- #

        device = get_device_information(request)

        trusted_device = TrustedDevice.objects.filter(
            user=user,
            browser=device["browser"],
            operating_system=device["operating_system"],
            ip_address=device["ip_address"],
            is_active=True,
        ).first()

        # ---------------- Trusted Device Exists ---------------- #

        if trusted_device:

            if trusted_device.is_expired():

                trusted_device.is_active = False
                trusted_device.save()

                otp = create_device_otp(
                    user,
                    device,
                )

                send_device_otp(
                    user.email,
                    otp,
                )

                request.session["pending_2fa_user"] = user.id

                messages.info(
                    request,
                    "This trusted device has expired. A verification OTP has been sent to your email."
                )

                return redirect(
                    "accounts:device_otp"
                )

            trusted_device.last_login = timezone.now()

            trusted_device.remember_until = (
                timezone.now()
                + timedelta(days=30)
            )

            trusted_device.save()

            login(
                request,
                user
            )

        # ---------------- New Device ---------------- #

        else:

            otp = create_device_otp(
                user,
                device,
            )

            send_device_otp(
                user.email,
                otp,
            )

            request.session["pending_2fa_user"] = user.id

            messages.success(
                request,
                "A verification OTP has been sent to your email."
            )

            return redirect(
                "accounts:device_otp"
            )

        # ---------------- Dashboard ---------------- #

        if user.role == "principal":

            return redirect(
                "academic:dashboard"
            )

        return redirect(
            "dashboard"
        )

    return render(
        request,
        "login.html"
    )


def teacher_logout(request):

    logout(request)

    return redirect(
        "accounts:login"
    )