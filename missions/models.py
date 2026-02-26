from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone


class MissionGoal(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "진행 중"
        COMPLETED = "COMPLETED", "완료"
        CANCELLED = "CANCELLED", "포기"  # 추가

    # 어떤 아이의 목표인가?
    child = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mission_goals"
    )
    title = models.CharField(max_length=200)
    target_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("1"))],  # 0원 목표 방지
    )
    deadline = models.DateField()  # >= today
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )

    # ─ 완료/포기 시 스냅샷
    # 진행 중 → null
    # 완료/포기 → 그 시점의 저축금액 저장
    # 완료 후, 저축계좌에서 돈을 꺼내도 "달성 당시 얼마 모았는지"는 변하지 않아야 하므로 !!
    snapshot_saved_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="완료·포기 시점의 저축 금액 스냅샷. 진행 중엔 null.",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="완료 또는 포기 처리된 시각.",
    )
    # - 이력 추적
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # - 유효성 검증
    def clean(self):
        # 마감일은 오늘 포함 허용
        today = timezone.localdate()
        if self.deadline and self.deadline < today:
            raise ValidationError(
                {"deadline": "마감일은 오늘 이후(오늘 포함)여야 합니다."}
            )

        # 상태-스냅샷 불변식
        if self.status == self.Status.IN_PROGRESS:
            if self.snapshot_saved_amount is not None or self.completed_at is not None:
                raise ValidationError(
                    "진행 중 목표는 snapshot_saved_amount/completed_at이 비어 있어야 합니다."
                )
        else:
            if self.snapshot_saved_amount is None or self.completed_at is None:
                raise ValidationError(
                    "완료/포기 목표는 snapshot_saved_amount/completed_at이 필요합니다."
                )

    # ── 계산 프로퍼티 ──
    @property
    def current_save_amount(self) -> Decimal:
        """
        진행 중 -> 저축계좌 전체 잔액 합산(실시간 계산)
        완료/ 포기 -> 당시 스냅샷 반환(고정)
        """
        if self.snapshot_saved_amount is not None:
            return self.snapshot_saved_amount

        from assets.models import Asset

        return Asset.objects.filter(
            user=self.child,
            is_active=True,
            is_saving_account=True,
        ).aggregate(total=Coalesce(Sum("balance"), Decimal("0")))["total"]

    @property
    def progress_rate(self) -> float:
        """
        현재 저축 진행률을 계산 퍼센티지 (0 ~ 100)
        """
        if self.target_price <= 0:
            return 0.0  # Zero Division 방지
        # 소수점 첫째 자리까지만 반환
        return round(float(self.current_save_amount / self.target_price * 100), 1)

    @property
    def days_left(self) -> int:
        """
        마감일까지 남은 일수
        양수 → 아직 여유 있음
        0    → 오늘이 마감일
        음수 → 마감일 지남
        """
        return (self.deadline - timezone.localdate()).days

    # ── 상태 전환 메서드 ──
    # ⚠️ views.py에서 직접 status = "COMPLETED" 하지 말자 !!!
    # 반드시 이 메서드를 통해야 스냅샷이 보장됨

    def complete(self):
        """목표 완료 처리."""
        if self.status != self.Status.IN_PROGRESS:
            raise ValidationError("진행 중인 목표만 완료할 수 있습니다.")
        self.snapshot_saved_amount = self.current_save_amount
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(
            update_fields=[
                "snapshot_saved_amount",
                "status",
                "completed_at",
                "updated_at",
            ]
        )

    def cancel(self):
        """목표 포기 처리."""
        if self.status != self.Status.IN_PROGRESS:
            raise ValidationError("진행 중인 목표만 포기할 수 있습니다.")
        self.snapshot_saved_amount = self.current_save_amount
        self.status = self.Status.CANCELLED
        self.completed_at = timezone.now()
        self.save(
            update_fields=[
                "snapshot_saved_amount",
                "status",
                "completed_at",
                "updated_at",
            ]
        )

    def __str__(self):
        return f"{self.child.username} - {self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # 모델 단독 저장 시에도 clean()/제약 검증을 강제

        # update_fields로 부분 저장할 때는 full_clean 건너뜀
        # complete(), cancel() 메서드가 이미 검증하므로 안전
        if not kwargs.get("update_fields"):
            self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "mission_goal"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["child"],
                condition=models.Q(status="IN_PROGRESS"),
                name="uniq_in_progress_goal_per_child",
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(status="IN_PROGRESS")
                    | (
                        models.Q(snapshot_saved_amount__isnull=True)
                        & models.Q(completed_at__isnull=True)
                    )
                ),
                name="chk_in_progress_fields_null",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(status="IN_PROGRESS")
                    | (
                        models.Q(snapshot_saved_amount__isnull=False)
                        & models.Q(completed_at__isnull=False)
                    )
                ),
                name="chk_done_fields_not_null",
            ),
        ]
