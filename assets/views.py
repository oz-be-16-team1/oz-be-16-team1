from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Asset
from .serializers import AssetSerializer, AssetUpdateSerializer


class AssetListCreateView(APIView):
    """
    GET  /assets/   → 내 자산 목록 조회
    POST /assets/   → 새 자산 생성
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # is_active=True인 것만 보여주기 (Soft Delete 적용)
        assets = Asset.objects.filter(user=request.user, is_active=True)
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AssetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # user는 read_only라 클라이언트가 못 넣으니
        # 여기서 로그인한 유저를 직접 넣어줌
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AssetDetailView(APIView):
    """
    GET    /assets/<id>/  → 특정 자산 조회
    PATCH  /assets/<id>/  → 자산 수정 (부분 수정)
    DELETE /assets/<id>/  → 자산 삭제 (Soft Delete)
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        # 타인의 자산 조회/삭제 막기위해 user 조건 걸기
        try:
            return Asset.objects.get(pk=pk, user=user, is_active=True)
        except Asset.DoesNotExist:
            return None

    def get(self, request, pk):
        asset = self.get_object(pk, request.user)
        if not asset:
            return Response(
                {"detail": "자산을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = AssetSerializer(asset)
        return Response(serializer.data)

    def patch(self, request, pk):
        asset = self.get_object(pk, request.user)
        if not asset:
            return Response(
                {"detail": "자산을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = AssetUpdateSerializer(asset, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AssetSerializer(asset).data)

    def delete(self, request, pk):
        asset = self.get_object(pk, request.user)
        if not asset:
            return Response(
                {"detail": "자산을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND
            )
        # 실제로 DB에서 지우는 게 아니라
        # is_active를 False로 바꾸는 Soft Delete
        asset.is_active = False
        asset.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
