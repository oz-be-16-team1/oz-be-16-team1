from rest_framework import serializers
from assets.models import Asset


class AssetSerializer(serializers.ModelSerializer):
    # user는 로그인한 사람의 정보를 서버에서 자동으로 넣기
    # read_only=True
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate_balance(self, value):
        # 잔액 음수 방지
        if value < 0:
            raise serializers.ValidationError("잔액이 음수일 수 없습니다.")
        return value

    def validate_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("자산 이름은 공백일 수 없습니다.")
        return cleaned

    def validate_asset_type(self, value):
        if value not in Asset.AssetType.values:
            raise serializers.ValidationError("올바르지 않은 자산 유형입니다.")
        return value

    class Meta:
        model = Asset
        # is_activate는 클라이언트 직접수정 불가능하게
        # 삭제는 DELETE 요청으로만 처리해서 제외
        fields = [
            "id",
            "user",
            "asset_type",
            "name",
            "provider",
            "balance",
            "display_number",
            "encrypted_number",
            "is_saving_account",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "provider": {"required": False, "allow_blank": True},
            "display_number": {"required": False, "allow_blank": True},
            "encrypted_number": {
                "required": False,
                "allow_blank": True,
                "write_only": True,
            },
            "is_saving_account": {"required": False},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }


class AssetUpdateSerializer(serializers.ModelSerializer):
    ALLOWED_FIELDS = {"name", "balance"}

    def validate(self, attrs):
        disallowed = set(self.initial_data.keys()) - self.ALLOWED_FIELDS
        if disallowed:
            raise serializers.ValidationError(
                {"non_field_errors": ["name과 balance만 수정할 수 있습니다."]}
            )
        return attrs

    def validate_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("잔액이 음수일 수 없습니다.")
        return value

    def validate_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("자산 이름은 공백일 수 없습니다.")
        return cleaned

    class Meta:
        model = Asset
        fields = ["name", "balance"]
        extra_kwargs = {
            "name": {"required": False},
            "balance": {"required": False},
        }
