from django.db import models
from django.conf import settings


class MoneyProverb(models.Model):
    content = models.TextField()  # 명언 내용
    author = models.CharField(max_length=100, default="익명")
    # 추가하면 좋은 필드들
    category = models.CharField(max_length=50, default="저축")  # 저축, 투자, 소비 등

    def __str__(self):
        return f"{self.author}: {self.content[:20]}..."


class ProverbScrap(models.Model):
    # 사용자가 어떤 명언을 스크랩했는지 기록
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    proverb = models.ForeignKey(MoneyProverb, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "proverb")  # 중복 스크랩 방지
