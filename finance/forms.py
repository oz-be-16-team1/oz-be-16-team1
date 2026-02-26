from django.contrib.auth import forms

from finance.models import Transaction


class TransactionCreateForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "asset",
            "amount",
            "store_name",
            "category",
            "category_middle",
            "etc",
            "is_confirmed",
            "importance",
            "memo",
            "is_fixed_expense",
            "real_date",
        ]
        widgets = {
            "real_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "memo": forms.Textarea(attrs={"rows": 3}),
        }
