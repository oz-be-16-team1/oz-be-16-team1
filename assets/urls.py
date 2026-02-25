from django.urls import path
from .views import AssetListCreateView, AssetDetailView

urlpatterns = [
    path("", AssetListCreateView.as_view(), name="asset-list-create"),
    path("<int:pk>/", AssetDetailView.as_view(), name="asset-detail"),
]
