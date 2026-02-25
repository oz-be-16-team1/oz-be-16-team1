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

    class Meta:
        model = Asset
        # is_activate는 클라이언트 직접수정 불가능하게
        # 삭제는 DELETE 요청으로만 처리해서 제외
        fields = ["id", "user", "asset_type", "name", "balance"]
