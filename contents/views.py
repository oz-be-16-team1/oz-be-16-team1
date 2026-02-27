from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.exceptions import ValidationError

from contents.models import MoneyProverb, ProverbScrap
from contents.serializers import MoneyProverbSerializer, ProverbScrapSerializer


# 명언 출력
class ContentsMoneyProverbListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # 저장된 명언 랜덤 출력
    def get(self, request):
        ojb = MoneyProverb.objects.all().order_by("?").first()
        serializer = MoneyProverbSerializer(ojb)
        return Response(serializer.data)


class ProverbScrapListCreateView(viewsets.ModelViewSet):
    serializer_class = ProverbScrapSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = ["get", "post", "delete"]

    # 관심 등록한 명언 출력
    def get_queryset(self):
        return (
            ProverbScrap.objects.filter(user=self.request.user)
            .select_related("proverb")
            .order_by("-created_at")
        )

    # 명언 관심 등록 추가
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        proverb_id = request.data.get("proverb_id") or request.data.get("proverb")
        if proverb_id in (None, ""):
            raise ValidationError({"proverb_id": ["이 필드는 필수입니다."]})

        proverb = get_object_or_404(MoneyProverb, pk=proverb_id)

        serializer = self.get_serializer(data={"proverb_id": proverb.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, proverb=proverb)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
