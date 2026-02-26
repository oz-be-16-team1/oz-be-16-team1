from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="사자사자 가계부 API명세서",
        default_version="v1",
        description="사자사자 가계부의 API명세서입니다.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # API
    path("api/users/", include("users.urls")),
    path("api/assets/", include("assets.urls")),
    path("api/missions/", include("missions.urls")),
    path("api/finance/", include("finance.urls")),
    path("api/contents/", include("contents.urls")),
    # Web
    path("", RedirectView.as_view(pattern_name="users:login")),
    # Docs
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
