from django.db import models
from django.conf import settings


class MissionGoal(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "진행 중"
        COMPLETED = "COMPLETED", "완료"

    # 어떤 아이의 목표인가?
    child = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mission_goals"
    )

    title = models.CharField(max_length=200)  # 예: 닌텐도 사기
    target_price = models.DecimalField(max_digits=12, decimal_places=0)
    saved_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    deadline = models.DateField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.IN_PROGRESS
    )


class GoalAlbum(models.Model):
    # 어떤 목표에 속한 앨범인지
    goal = models.ForeignKey(
        MissionGoal, on_delete=models.CASCADE, related_name="albums"
    )

    image = models.ImageField(upload_to="goal_albums/")  # 과정 인증샷
    child_memo = models.TextField(blank=True)
    parent_comment = models.TextField(blank=True)  # 부모의 코멘트 (응원 등)
    created_at = models.DateTimeField(auto_now_add=True)


@property
def progress_rate(self):
    """
    현재 저축 진행률을 계산 퍼센티지 (0 ~ 100)
    """
    if self.target_price <= 0:
        return 0  # Zero Division 방지

    # 진행률 계산 (일반 나눗셈 사용)
    rate = (self.saved_amount / self.target_price) * 100

    return round(rate, 1)  # 소수점 첫째 자리까지만 반환
