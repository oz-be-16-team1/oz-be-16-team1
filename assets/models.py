from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .security import encrypt_if_needed


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
    provider = models.CharField(max_length=100, blank=True, default="")
    balance = models.DecimalField(
        max_digits=13,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(0)],
    )
    display_number = models.CharField(max_length=20, blank=True, default="")
    encrypted_number = models.TextField(blank=True, default="")
    is_saving_account = models.BooleanField(default=False)

    # Soft Delete를 위해
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=0),
                name="asset_balance_gte_0",
            )
        ]

    def save(self, *args, **kwargs):
        if self.encrypted_number:
            self.encrypted_number = encrypt_if_needed(self.encrypted_number)
        super().save(*args, **kwargs)

    def __str__(self):
        username = self.user.username if self.user else "deleted-user"
        return f"[{self.get_asset_type_display()}] {self.name} ({username})"
