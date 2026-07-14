from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from datetime import timedelta
from django.utils import timezone
import secrets



class Teacher(AbstractUser):

    ROLE_CHOICES = (
        ("teacher", "Teacher"),
        ("principal", "Principal / HOD"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="teacher"
    )

    department = models.CharField(
        max_length=100,
        blank=True
    )

    email = models.EmailField(
        unique=True
    )

    phone_number = models.CharField(
        max_length=15,
        unique=True
    )

    is_phone_verified = models.BooleanField(
        default=False
    )

    is_email_verified = models.BooleanField(
        default=False
    )

    remember_device = models.BooleanField(
        default=False
    )

    last_device = models.CharField(
        max_length=255,
        blank=True
    )

    last_ip = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["first_name"]

    def __str__(self):
        return f"{self.first_name} ({self.get_role_display()})"
    



class PasswordOTP(models.Model):

    user = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE
    )

    otp = models.CharField(
        max_length=6
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_verified = models.BooleanField(
        default=False
    )
    attempts = models.PositiveIntegerField(
    default=0
    )

    def is_expired(self):

        return (
            timezone.now()
            >
            self.created_at
            +
            timedelta(minutes=10)
        )

    def __str__(self):

        return f"{self.user.email} - {self.otp}"
    




class EmailVerification(models.Model):

    user = models.OneToOneField(
        Teacher,
        on_delete=models.CASCADE,
        related_name="email_verification"
    )

    token = models.CharField(
        max_length=100,
        unique=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    def save(self, *args, **kwargs):

        if not self.token:
            self.token = secrets.token_urlsafe(32)

        super().save(*args, **kwargs)

    def is_expired(self):

        return (
            timezone.now()
            >
            self.created_at
            +
            timedelta(hours=24)
        )

    def __str__(self):

        return self.user.email

# class EmailVerification(models.Model):

#     user = models.OneToOneField(
#         Teacher,
#         on_delete=models.CASCADE,
#         related_name="email_verification"
#     )

#     token = models.CharField(
#         max_length=100,
#         unique=True
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True
#     )

#     is_verified = models.BooleanField(
#         default=False
#     )

#     def is_expired(self):
#         return (
#             timezone.now() >
#             self.created_at + timedelta(hours=24)
#         )

#     def save(self, *args, **kwargs):

#         if not self.token:
#             self.token = secrets.token_urlsafe(32)

#         super().save(*args, **kwargs)    



class TrustedDevice(models.Model):

    user = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="trusted_devices"
    )

    device_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    device_name = models.CharField(
        max_length=255
    )

    browser = models.CharField(
        max_length=100
    )

    operating_system = models.CharField(
        max_length=100
    )

    ip_address = models.GenericIPAddressField()

    remember_until = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    last_login = models.DateTimeField(
        auto_now=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:

        ordering = [
            "-last_login"
        ]

    def is_expired(self):

        return timezone.now() > self.remember_until

    def __str__(self):

        return (
            f"{self.user.email} - "
            f"{self.device_name}"
        )   
class DeviceOTP(models.Model):
    
    user = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="device_otps"
    )

    otp = models.CharField(
        max_length=6
    )

    device_name = models.CharField(
        max_length=255
    )

    browser = models.CharField(
        max_length=100
    )

    operating_system = models.CharField(
        max_length=100
    )

    ip_address = models.GenericIPAddressField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    attempts = models.PositiveIntegerField(
        default=0
    )

    class Meta:

        ordering = [
            "-created_at"
        ]

    def is_expired(self):

        return (
            timezone.now()
            >
            self.created_at
            +
            timedelta(minutes=10)
        )

    def __str__(self):

        return (
            f"{self.user.email} - "
            f"{self.browser}"
        )         