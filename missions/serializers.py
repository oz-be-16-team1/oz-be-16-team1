from rest_framework import serializers

from missions.models import GoalComment, MissionGoal


class MissionGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionGoal
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class GoalCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalComment
        fields = "__all__"
        read_only_fields = ("id", "created_at")
