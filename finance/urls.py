from django.urls import path, include
from rest_framework.routers import DefaultRouter
from finance import views

name = "finance"
router = DefaultRouter()
router.register(
    r"transaction", views.TransactionListCreateAPIView, basename="transaction"
)
router.register(r"fixed", views.FixedExpenseListCreateAPIView, basename="fixed")

urlpatterns = [
    path("", include(router.urls)),
]
