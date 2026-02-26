from rest_framework import serializers

from contents.models import MoneyProverb, ProverbScrap


class MoneyProverbSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyProverb
        fields = "__all__"
        read_only_fields = ["content", "author"]


class ProverbScrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProverbScrap
        fields = "__all__"

    def validate(self, data):
        # 로그인 한 유저 정보 가져오기
        user = self.context["request"].user
        # 입력한 proverb 값 가져오기
        proverb = data.get("proverb")

        # 이미 등록한 명언이면 중복 에러
        if ProverbScrap.objects.filter(user=user, proverb=proverb).exists():
            raise serializers.ValidationError("이미 등록한 명언입니다.")

        return data
