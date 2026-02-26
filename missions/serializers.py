from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from .models import MissionGoal


class MissionGoalSerializer(serializers.ModelSerializer):
    """
    목록 조회 / 상세 조회용 Serializer
    current_save_amount, progress_rate, days_left는 읽기 전용 계산값
    """

    current_save_amount = serializers.SerializerMethodField()
    progress_rate = serializers.SerializerMethodField()
    days_left = serializers.SerializerMethodField()

    def get_current_save_amount(self, obj) -> Decimal:
        return obj.current_save_amount

    def get_progress_rate(self, obj) -> float:
        return obj.progress_rate

    def get_days_left(self, obj) -> int:
        return obj.days_left

    class Meta:
        model = MissionGoal
        fields = [
            "id",
            "title",
            "target_price",
            "deadline",
            "status",
            "snapshot_saved_amount",
            "completed_at",
            "created_at",
            "updated_at",
            # 계산 프로퍼티 (읽기 전용)
            "current_save_amount",
            "progress_rate",
            "days_left",
        ]
        read_only_fields = [
            "status",  # 상태는 complete()/cancel() 메서드로만 변경
            "snapshot_saved_amount",
            "completed_at",
            "created_at",
            "updated_at",
        ]


class MissionGoalCreateSerializer(serializers.ModelSerializer):
    """
    목표 생성 전용 Serializer
    - child는 로그인 유저로 자동 주입 (read_only)
    - 활성 목표 1개 제약 검증
    - 마감일 과거 날짜 방지
    """

    class Meta:
        model = MissionGoal
        fields = ["id", "title", "target_price", "deadline"]

    def _get_request_user(self):
        request = self.context.get("request")
        if request is None or not hasattr(request, "user"):
            raise serializers.ValidationError("요청 사용자 정보가 필요합니다.")
        return request.user

    def validate_target_price(self, value):
        if value < Decimal("1"):
            raise serializers.ValidationError("목표 금액은 1원 이상이어야 합니다")
        return value

    def validate_deadline(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError(
                "마감일은 오늘 이후(오늘 포함)여야 합니다."
            )
        return value

    def validate(self, data):
        # 활성 목표 1개 제약
        # UniqueConstraint가 DB 레벨에서도 막지만 사용자 친화적인 에러 메시지를 위해 여기서도 검증
        child = self._get_request_user()
        already_exists = MissionGoal.objects.filter(
            child=child,
            status=MissionGoal.Status.IN_PROGRESS,
        ).exists()
        if already_exists:
            raise serializers.ValidationError(
                "이미 진행 중인 목표가 있습니다! 기존 목표를 완료하거나 포기해주세요."
            )
        return data

    def create(self, validated_data):
        validated_data["child"] = self._get_request_user()
        return super().create(validated_data)


class MissionGoalUpdateSerializer(serializers.ModelSerializer):
    """
    목표 수정 전용 Serializer
    - 진행 중인 목표만 수정 가능
    - title, target_price, deadline만 수정 허용
    - status 직접 수정 불가 (complete()/cancel() 메서드로만)
    """

    class Meta:
        model = MissionGoal
        fields = ["title", "target_price", "deadline"]

    def validate_target_price(self, value):
        if value < Decimal("1"):
            raise serializers.ValidationError("목표 금액은 1원 이상이어야 합니다.")
        return value

    def validate_deadline(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError(
                "마감일은 오늘 이후(오늘 포함)여야 합니다."
            )
        return value

    def validate(self, data):
        # 완료/포기된 목표는 수정 불가
        if self.instance.status != MissionGoal.Status.IN_PROGRESS:
            raise serializers.ValidationError("진행 중인 목표만 수정할 수 있습니다.")
        return data
