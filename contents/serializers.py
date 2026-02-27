from rest_framework import serializers

from contents.models import MoneyProverb, ProverbScrap


class MoneyProverbSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyProverb
        fields = "__all__"
        read_only_fields = ["content", "author"]


class ProverbScrapSerializer(serializers.ModelSerializer):
    proverb = MoneyProverbSerializer(read_only=True)
    proverb_id = serializers.PrimaryKeyRelatedField(
        queryset=MoneyProverb.objects.all(),
        source="proverb",
        write_only=True,
    )

    class Meta:
        model = ProverbScrap
        fields = ("id", "created_at", "proverb", "proverb_id")
        read_only_fields = ("user",)

    def to_internal_value(self, data):
        # 기존 클라이언트 호환: proverb(숫자 ID) 입력을 proverb_id로 매핑
        if isinstance(data, dict) and "proverb" in data and "proverb_id" not in data:
            data = data.copy()
            data["proverb_id"] = data["proverb"]
        return super().to_internal_value(data)

    def validate(self, data):
        # 로그인 한 유저 정보 가져오기
        user = self.context["request"].user
        # 입력한 proverb 값 가져오기
        proverb = data.get("proverb")

        # 이미 등록한 명언이면 중복 에러
        if ProverbScrap.objects.filter(user=user, proverb=proverb).exists():
            raise serializers.ValidationError("이미 등록한 명언입니다.")

        return data
