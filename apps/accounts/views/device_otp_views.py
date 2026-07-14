from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.utils import timezone

from apps.accounts.device_utils import get_device_information
from apps.accounts.models import (
    Teacher,
    DeviceOTP,
    TrustedDevice,
)


def device_otp(request):
    user_id = request.session.get("pending_2fa_user")

    if not user_id:
        messages.error(request, "Session expired.")
        return redirect("accounts:login")

    try:
        user = Teacher.objects.get(id=user_id)
    except Teacher.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("accounts:login")

    if request.method == "POST":
        otp = request.POST.get("otp")

        try:
            otp_obj = DeviceOTP.objects.get(
                user=user,
                otp=otp,
            )
        except DeviceOTP.DoesNotExist:
            messages.error(request, "Invalid OTP.")
            return redirect("accounts:device_otp")

        # OTP expired
        if otp_obj.is_expired():
            otp_obj.delete()
            messages.error(request, "OTP expired.")
            return redirect("accounts:login")

        # OTP already used
        if otp_obj.is_verified:
            messages.error(request, "OTP already used.")
            return redirect("accounts:login")

        # Verify OTP
        otp_obj.is_verified = True
        otp_obj.save()

        # Current device
        device = get_device_information(request)

        # Save trusted device
        trusted_device, created = TrustedDevice.objects.get_or_create(
            user=user,
            browser=device["browser"],
            operating_system=device["operating_system"],
            ip_address=device["ip_address"],
            defaults={
                "device_name": device["device_name"],
                "remember_until": timezone.now() + timedelta(days=30),
            },
        )

        if not created:
            trusted_device.device_name = device["device_name"]
            trusted_device.last_login = timezone.now()
            trusted_device.remember_until = timezone.now() + timedelta(days=30)
            trusted_device.is_active = True
            trusted_device.save()

        # Login user
        login(request, user)

        # Delete OTP
        otp_obj.delete()

        # Remove session
        request.session.pop("pending_2fa_user", None)

        messages.success(
            request,
            "Device verified successfully."
        )

        # Redirect according to role
        if user.role == "principal":
            return redirect("academic:dashboard")

        return redirect("dashboard")

    return render(
        request,
        "registration/device_otp.html",
    )