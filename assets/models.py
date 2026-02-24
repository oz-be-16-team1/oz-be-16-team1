from django.conf import settings
from django.db import models


class Asset(models.Model):
    class AssetType(models.TextChoices):
        BANK = "BANK", "은행"
        CREDIT_CARD = "CREDIT_CARD", "신용카드"
        PREPAID_CARD = "PREPAID_CARD", "신불카드"
        CASH = "CASH", "현금"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    asset_type = models.CharField(max_length=20, choices=AssetType.choices)
    name = models.CharField(max_length=100)  # "내 용돈 통장"
    provider = models.CharField(max_length=100, blank=True)  # "카카오뱅크"
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    display_number = models.CharField(max_length=20, blank=True)  # "**1234"
    encrypted_number = models.TextField(max_length=255, blank=True)  # AES 암호화된 값
    is_auto_sync = models.BooleanField(default=False)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        # 관리자 페이지나 디버깅할 때 알아보기 쉽게
        return f"{self.user} - {self.name} ({self.asset_type})"
