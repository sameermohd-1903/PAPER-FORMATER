import resend
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _send_email(to_email, subject, message):
    api_key = settings.RESEND_API_KEY

    if not api_key:
        raise ImproperlyConfigured("RESEND_API_KEY is not configured.")

    resend.api_key = api_key

    resend.Emails.send(
        {
            "from": "onboarding@resend.dev",
            "to": [to_email],
            "subject": subject,
            "text": message,
        }
    )


def send_password_otp(email, otp):

    subject = "Paper Formatter - Password Reset OTP"

    message = f"""
Hello,

You requested to reset your password.

Your One-Time Password (OTP) is:

{otp}

This OTP is valid for 10 minutes.

Do not share this OTP with anyone.

Regards,
Paper Formatter Team
"""

    _send_email(email, subject, message)


def send_verification_email(user, token):

    verification_link = (
        f"http://127.0.0.1:8000/accounts/verify-email/{token}/"
    )

    subject = "Verify Your Email - Paper Formatter"

    message = f"""
Hello {user.first_name},

Welcome to Paper Formatter!

Please verify your email by clicking the link below:

{verification_link}

This link is valid for 24 hours.

If you did not create this account, please ignore this email.

Regards,
Paper Formatter Team
"""

    _send_email(user.email, subject, message)


def send_device_otp(email, otp):

    subject = "Paper Formatter - New Device Verification"

    message = f"""
Hello,

A login attempt was detected from a new or untrusted device.

Your verification code is:

{otp}

This OTP is valid for 10 minutes.

If this wasn't you, please change your password immediately.

Regards,
Paper Formatter Team
"""

    _send_email(email, subject, message)