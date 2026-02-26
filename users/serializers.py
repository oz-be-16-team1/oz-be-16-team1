from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
import uuid


class RegisterSerializer(serializers.ModelSerializer):
    # 비밀번호는 쓰기 전용으로 설정 for 조회 시 노출 방지
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "role", "parent"]

    # 필드 수준 검정 (validate_<필드명>)
    def validate(self, data):
        role = data.get("role", None)
        parent = data.get("parent", None)
        email = data.get("email")

        if role is None:
            raise serializers.ValidationError({"role": "role은 필수입니다."})

        if not email:
            raise serializers.ValidationError({"email": "email은 필수입니다."})

            # 역할이 부모인 유저 (role: parent) 는 자신의 부모를 가질 수 없도록 제한
        # 최적의 방법은 아닌것 같지만
        if role == User.RoleEnum.PARENT and parent is not None:
            raise serializers.ValidationError(
                "부모 역할은 상위 부모를 가질 수 없습니다."
            )
        return data

    def create(self, validated_data):
        # 유저 생성 시 비밀번호를 암호화하여 저장
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data.get("role", "child"),
            parent=validated_data.get("parent", None),
            is_active=False,  # 이메일 인증 전까지 로그인 제한
            verification_token=str(uuid.uuid4()),  # 토큰 생성
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # 토큰에 추가 클레임 설정
        token["username"] = user.username
        token["email"] = user.email
        token["role"] = user.role

        return token
