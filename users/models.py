from django.contrib.auth.models import AbstractUser
import uuid
from django.db import models


class User(AbstractUser):
    class RoleEnum(models.TextChoices):
        PARENT = "PARENT", "부모"
        CHILD = "CHILD", "자녀"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10, choices=RoleEnum.choices, default=RoleEnum.PARENT
    )
    # 이메일 인증 여부 확인 필드
    is_email_verified = models.BooleanField(default=False)
    # 이메일 인증용 고유 토큰 (간단한 구현을 위해 UUID 등 사용 가능)
    verification_token = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )
    # 자기 참조 (부모-자녀 연결) / 부모 계정은 이 필드가 null
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )

    birth_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)  ## 법정대리인 동의 여부 ##
    allow_monitoring = models.BooleanField(default=True)  # 자녀의 독립 토글

    def resign_user(self):
        """
        사용자 탈퇴 처리:
        1. 사용자의 is_active를 False로 변경
        2. 연결된 모든 자산(Asset)의 is_active를 False로 변경
        """
        # 1. 사용자 비활성화 (Soft Delete)
        self.is_active = False
        self.save()

        # 2. 연결된 자산들 일괄 비활성화
        # related_name='assets'를 활용합니다.
        self.assets.all().update(is_active=False)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
