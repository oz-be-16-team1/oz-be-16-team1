from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views


app_name = "users"  # 템플릿 등에서 'users:login'으로 호출 가능

urlpatterns = [
    # /api/users/ 로 접속하면 바로 login/ 으로 보냄
    path("", RedirectView.as_view(url="login/"), name="index"),
    path("verify/<str:token>/", views.verify_email, name="verify_email"),
    path("resend-email/", views.resend_verification, name="resend_verification"),
    path("main/", views.main_home, name="main"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="api_login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
    # API Endpoints
    path("api/register/", views.RegisterView.as_view(), name="api_register"),
    path(
        "api/verify/<str:token>/",
        views.VerifyEmailView.as_view(),
        name="api_verify_email",
    ),
    path("api/login/", views.LoginView.as_view(), name="api_login"),
    path("api/logout/", views.LogoutView.as_view(), name="api_logout"),
]
