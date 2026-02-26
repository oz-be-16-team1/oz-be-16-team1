from django.contrib import admin

from contents.models import MoneyProverb, ProverbScrap


@admin.register(MoneyProverb)
class ContentAdmin(admin.ModelAdmin):
    class Media:
        model = MoneyProverb


@admin.register(ProverbScrap)
class ProverbScrapAdmin(admin.ModelAdmin):
    class Media:
        model = ProverbScrap
