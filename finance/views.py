from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from assets.models import Asset
from finance.models import Transaction, FixedExpense
from finance.serializers import TransactionSerializer, FixedExpenseSerializer


# 거래 정보
class TransactionListCreateAPIView(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    # 거래 정보 출력
    def get_queryset(self):
        user = self.request.user

        # 조회자가 부모일 경우
        if user.role == "PARENT":
            return (
                Transaction.objects.filter(Q(user=user) | Q(user__parent=user))
                .select_related("asset")
                .order_by("-created_at")
            )

        else:
            # 부모가 아니라면
            return (
                Transaction.objects.filter(user=user)
                .select_related("asset")
                .order_by("-created_at")
            )

    # 수정 삭제 상세조회 등 단일 객체 하나를 건드릴때 적용
    def get_object(self):
        obj = super().get_object()
        user = self.request.user

        if obj.user != user and self.request.method not in SAFE_METHODS:
            raise PermissionDenied("수정/삭제는 작성자만 가능합니다.")

        return obj

    # 거래 정보 추가
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

    # 거래 정보 수정
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


# 정기 구독
class FixedExpenseListCreateAPIView(viewsets.ModelViewSet):
    serializer_class = FixedExpenseSerializer
    permission_classes = [IsAuthenticated]

    # 정기 구독 출력
    def get_queryset(self):
        return FixedExpense.objects.filter(user=self.request.user).order_by(
            "-payment_day"
        )

    # 정기 구독 추가
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # 정기 구독 수정
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
