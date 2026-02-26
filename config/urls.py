from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),  # users 앱
    # http://localhost:8000/ 접속 시 로그인 페이지로 이동
    path("", RedirectView.as_view(pattern_name="users:login")),
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/assets/", include("assets.urls")),
    path("api/contents/", include("contents.urls")),
    path("api/finance/", include("finance.urls")),
]
