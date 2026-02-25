from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from contents.models import MoneyProverb, ProverbScrap
from contents.serializers import MoneyProverbSerializer, ProverbScrapSerializer


class ContentsMoneyProverbListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        ojb = MoneyProverb.objects.all().order_by("?").first()
        serializer = MoneyProverbSerializer(ojb, many=True)
        return Response(serializer.data)


class ProverbScrapListCreateView(viewsets.ModelViewSet):
    serializer_class = ProverbScrapSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            ProverbScrap.objects.filter(user=self.request.user)
            .select_related("proverb")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user, property_id=self.kwargs.get("proverb_id")
        )
