from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MissionGoal
from .serializers import (
    MissionGoalCreateSerializer,
    MissionGoalSerializer,
    MissionGoalUpdateSerializer,
)


class MissionGoalListCreateView(APIView):
    """
    GET  /missions/         → 내 목표 목록 조회 (전체 이력)
    POST /missions/         → 새 목표 생성
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        goals = MissionGoal.objects.filter(child=request.user)
        serializer = MissionGoalSerializer(goals, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MissionGoalCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MissionGoalDetailView(APIView):
    """
    GET    /missions/<id>/          → 특정 목표 상세 조회
    PATCH  /missions/<id>/          → 목표 수정 (title, target_price, deadline)
    DELETE /missions/<id>/          → 목표 삭제 (Hard Delete)
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return MissionGoal.objects.get(pk=pk, child=user)
        except MissionGoal.DoesNotExist:
            return None

    def get(self, request, pk):
        goal = self.get_object(pk, request.user)
        if not goal:
            return Response(
                {"detail": "목표를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = MissionGoalSerializer(goal)
        return Response(serializer.data)

    def patch(self, request, pk):
        goal = self.get_object(pk, request.user)
        if not goal:
            return Response(
                {"detail": "목표를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = MissionGoalUpdateSerializer(goal, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(MissionGoalSerializer(goal).data)

    def delete(self, request, pk):
        goal = self.get_object(pk, request.user)
        if not goal:
            return Response(
                {"detail": "목표를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        goal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MissionGoalCompleteView(APIView):
    """
    POST /missions/<id>/complete/   → 목표 완료 처리
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            goal = MissionGoal.objects.get(pk=pk, child=request.user)
        except MissionGoal.DoesNotExist:
            return Response(
                {"detail": "목표를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            goal.complete()
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(MissionGoalSerializer(goal).data)


class MissionGoalCancelView(APIView):
    """
    POST /missions/<id>/cancel/     → 목표 포기 처리
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            goal = MissionGoal.objects.get(pk=pk, child=request.user)
        except MissionGoal.DoesNotExist:
            return Response(
                {"detail": "목표를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            goal.cancel()
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(MissionGoalSerializer(goal).data)
