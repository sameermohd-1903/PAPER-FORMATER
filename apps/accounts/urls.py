from django.urls import path
from django.contrib.auth import views as auth_views

from .views.login_views import (
    teacher_login,
    teacher_logout,
)

from .views.registration_views import (
    TeacherRegisterView,
    principal_register,
)

from .views.dashboard_views import (
    dashboard,
    principal_dashboard,
)

from .views.password_views import (
    forgot_password,
    verify_otp,
    reset_password,
)
from .views.email_views import (
    verify_email_sent,
)
from .views.email_views import (
    verify_email,
)

from .views.email_views import (
    resend_verification_email,
)

from .views.device_otp_views import (
    device_otp,
)


app_name = "accounts"

urlpatterns = [

    # ---------------- Login ---------------- #

    path(
        "",
        teacher_login,
        name="login",
    ),

    path(
        "login/",
        teacher_login,
        name="login",
    ),

    path(
        "logout/",
        teacher_logout,
        name="logout",
    ),

    # ---------------- Registration ---------------- #

    path(
        "register/",
        TeacherRegisterView.as_view(),
        name="register",
    ),

    path(
        "principal-register/",
        principal_register,
        name="principal_register",
    ),

    # ---------------- Dashboard ---------------- #

    path(
        "dashboard/",
        dashboard,
        name="dashboard",
    ),

    path(
        "principal-dashboard/",
        principal_dashboard,
        name="principal_dashboard",
    ),

    # ---------------- Forgot Password ---------------- #

path(
    "forgot-password/",
    forgot_password,
    name="forgot_password",
),

# ---------------- Django Password Change ---------------- #

path(
    "password-change/",
    auth_views.PasswordChangeView.as_view(
        template_name="registration/password_change.html"
    ),
    name="password_change",
),

path(
    "password-change/done/",
    auth_views.PasswordChangeDoneView.as_view(
        template_name="registration/password_change_done.html"
    ),
    name="password_change_done",
),
path(
    "verify-otp/",
    verify_otp,
    name="verify_otp",
),   

path(
    "reset-password/",
    reset_password,
    name="reset_password",
),

path(
    "verify-email/<str:token>/",
    verify_email,
    name="verify_email",
),

path(
    "resend-verification/",
    resend_verification_email,
    name="resend_verification",
),

path(
    "device-otp/",
    device_otp,
    name="device_otp",
),

]