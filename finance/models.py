from django.db import models
from django.conf import settings


class Transaction(models.Model):
    # 관계 설정 / 어떤 아이의 내역인가?
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )

    # 관계 설정 / 어떤 자산에서 나갔는가?
    asset = models.ForeignKey(
        # 앱이름.모델명 문자열 참조로 순환참조 방지 !!!!
        "assets.Asset",
        on_delete=models.SET_NULL,
        null=True,
        related_name="transactions",
        blank=True,
    )

    # 금액 및 기본 정보
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    store_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)

    # 교육, 아이의 주체적 참여를 위한 필드
    is_confirmed = models.BooleanField(
        default=False
    )  # 아이가 스스로 확인하여 셀프 피드백 유도
    importance = models.PositiveSmallIntegerField(  # 평가 방법 별점(1-5)
        default=3, help_text="1~5점 사이의 중요도"
    )
    memo = models.TextField(null=True, blank=True)  # 셀프 피드백 기록

    ai_feedback = models.TextField(null=True, blank=True)

    # 고정 지출 여부
    is_fixed_expense = models.BooleanField(default=False)  # 고정비 여부
    # 메타 정보 (발생 일자)
    created_at = models.DateTimeField(auto_now_add=True)
    # 실제 일자
    real_date = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]  # 최신순 정렬

    def __str__(self):
        return f"{self.user.username} - {self.store_name}({self.amount}원)"


class FixedExpense(models.Model):
    """정기적으로 나가는 돈 (구독료 등)"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fixed_expenses",
    )
    title = models.CharField(max_length=100)  # 예: 넷플릭스
    amount = models.DecimalField(max_digits=13, decimal_places=0)
    payment_day = models.PositiveSmallIntegerField()  # 결제일 1~31일
    category = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} (매달 {self.payment_day}일)"
