from django.contrib import admin

from finance.models import Transaction


@admin.register(Transaction)
class TransactionProverbAdmin(admin.ModelAdmin):
    class Media:
        model = Transaction
