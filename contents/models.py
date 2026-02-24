from django.db import models


class MoneyProverb(models.Model):
    content = models.TextField()
    author = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.author} {self.content}"

    class Meta:
        verbose_name_plural = "MONEY PROVERB"


class ProverbScrap(models.Model):
    # uuid = models.ManyToManyField(User)
    proverb_id = models.ManyToManyField(MoneyProverb)
    created_at = models.DateTimeField(auto_now_add=True)
