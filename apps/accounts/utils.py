import random

from .models import PasswordOTP
import random

from .models import (PasswordOTP,EmailVerification,DeviceOTP)

from .models import PasswordOTP, DeviceOTP

def create_email_verification(user):
    """
    Create a fresh email verification token.
    """

    EmailVerification.objects.filter(
        user=user
    ).delete()

    verification = EmailVerification.objects.create(
        user=user
    )

    return verification


def generate_otp():
    """
    Generate a random 6-digit OTP.
    """

    return str(random.randint(100000, 999999))


def create_password_otp(user):
    """
    Create a fresh OTP for password reset.
    """

    # Delete old OTPs for this user
    PasswordOTP.objects.filter(
        user=user
    ).delete()

    otp = generate_otp()

    PasswordOTP.objects.create(
        user=user,
        otp=otp
    )

    return otp

def create_device_otp(
    user,
    device,
):
    """
    Create a fresh OTP for device verification.
    """

    DeviceOTP.objects.filter(
        user=user
    ).delete()

    otp = generate_otp()

    DeviceOTP.objects.create(
        user=user,
        otp=otp,
        device_name=device["device_name"],
        browser=device["browser"],
        operating_system=device["operating_system"],
        ip_address=device["ip_address"],
    )

    return otp