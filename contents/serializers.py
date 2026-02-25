from rest_framework import serializers

from contents.models import MoneyProverb, ProverbScrap


class MoneyProverbSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyProverb
        fields = "__all__"
        read_only_fields = ["content", "author"]


class ProverbScrapSerializer(serializers.ModelSerializer):
    # user =
    # proverb =

    class Meta:
        model = ProverbScrap
        fields = "__all__"
