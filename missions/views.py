from rest_framework import permissions, viewsets

from missions.models import GoalComment, MissionGoal
from missions.serializers import GoalCommentSerializer, MissionGoalSerializer


class MissionGoalViewSet(viewsets.ModelViewSet):
    serializer_class = MissionGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MissionGoal.objects.filter(child=self.request.user)

    def perform_create(self, serializer):
        serializer.save(child=self.request.user)


class GoalCommentViewSet(viewsets.ModelViewSet):
    serializer_class = GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalComment.objects.filter(mission_goal__child=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
