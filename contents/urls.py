from django.urls import path, include
from rest_framework.routers import DefaultRouter
from contents import views

router = DefaultRouter()
router.register(r"", views.ProverbScrapListCreateView, basename="proverb_scrap")

app_name = "contents"

urlpatterns = [
    path("proverb_scrap/", include(router.urls)),
    path("", views.ContentsMoneyProverbListView.as_view(), name="proverb_list"),
]
