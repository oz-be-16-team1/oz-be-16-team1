from django.db import models
from django.conf import settings


class Asset(models.Model):
    class AssetType(models.TextChoices):
        BANK = "bank", "계좌"
        CARD = "card", "신용카드"
        CASH = "cash", "현금"
        GIFTCARD = "giftcard", "선불카드"

    # 1:N 관계 설정
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # 사용자가 지워져도 자산 기록은 남김
        null=True,  # SET_NULL을 쓰려면 반드시 필요
        blank=True,
        related_name="assets",
    )

    asset_type = models.CharField(max_length=10, choices=AssetType.choices)
    name = models.CharField(max_length=50)  # 이름 : 예를들어 용돈 주머니
    balance = models.DecimalField(max_digits=13, decimal_places=0, default=0)

    # Soft Delete를 위해
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.get_asset_type_display()}] {self.name} ({self.user.username})"
