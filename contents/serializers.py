from rest_framework import serializers

from contents.models import MoneyProverb


class MoneySerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyProverb
        fields = "__all__"
        read_only_fields = ["content", "author"]
