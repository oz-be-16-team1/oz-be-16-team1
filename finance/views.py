from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from assets.models import Asset
from finance.models import Transaction, FixedExpense
from finance.serializers import TransactionSerializer, FixedExpenseSerializer


class TransactionListCreateAPIView(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # 조회자가 부모일 경우
        if user.role == "PARENT":
            user_children = user.parent.values_list("id", flat=True)

            return (
                Transaction.objects.filter(user__in=list(user_children) + [user.id])
                .select_related("asset")
                .order_by("-created_at")
            )

        else:
            # 부모가 아니라면
            return (
                Transaction.objects.filter(user=self.request.user)
                .select_related("asset")
                .order_by("-created_at")
            )

    def perform_create(self, serializer):
        asset_id = self.request.data.get("asset")

        if asset_id:
            asset = get_object_or_404(
                Asset,
                pk=asset_id,
                user=self.request.user,
            )

            serializer.save(user=self.request.user, asset=asset)

        else:
            serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class FixedExpenseListCreateAPIView(viewsets.ModelViewSet):
    serializer_class = FixedExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FixedExpense.objects.filter(user=self.request.user).order_by(
            "-payment_day"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
