from django.db import models


class Transaction(models.Model):
    # uuid = models.ForeignKey(Asset, on_delete=models.SET_NULL)
    # asset_id = models.ManyToManyField(User)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    store_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    is_confirmed = models.BooleanField(default=False, name="자녀 승인")
    importance = models.IntegerField(default=0)
    memo = models.TextField()
    ai_feedback = models.TextField()
    is_fixed_expense = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "TRANSACTION"
        ordering = ("-created_at",)
