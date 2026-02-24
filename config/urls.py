from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny

from assets.views import AssetViewSet
from missions.views import GoalCommentViewSet, MissionGoalViewSet

router = DefaultRouter()
router.register(r"assets", AssetViewSet, basename="asset")
router.register(r"missions/goals", MissionGoalViewSet, basename="mission-goal")
router.register(r"missions/comments", GoalCommentViewSet, basename="goal-comment")

schema_view = get_schema_view(
    openapi.Info(
        title="사자사자 가계부 API",
        default_version="v1",
        description="아이를 위한 부모-자녀 가계부 서비스 API",
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
