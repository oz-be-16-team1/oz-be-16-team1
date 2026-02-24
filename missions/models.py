from django.conf import settings
from django.db import models


class MissionGoal(models.Model):
    class GoalStatus(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELED = "CANCELED", "Canceled"

    child = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mission_goals",
    )
    title = models.CharField(max_length=200)
    target_price = models.DecimalField(max_digits=14, decimal_places=2)
    saved_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    parent_match_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    parent_matched_amount = models.DecimalField(
        max_digits=14, decimal_places=2, default=0
    )
    image_url = models.URLField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=GoalStatus.choices,
        default=GoalStatus.IN_PROGRESS,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title


class GoalComment(models.Model):
    class CommentType(models.TextChoices):
        CHEER = "CHEER", "Cheer"
        MATCH_OFFER = "MATCH_OFFER", "Match Offer"
        GENERAL = "GENERAL", "General"

    mission_goal = models.ForeignKey(
        MissionGoal,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="goal_comments",
    )
    content = models.TextField()
    comment_type = models.CharField(
        max_length=20,
        choices=CommentType.choices,
        default=CommentType.GENERAL,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"{self.user_id} - {self.comment_type}"
