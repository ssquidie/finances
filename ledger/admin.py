from django.contrib import admin
from .models import Entry, Profit, Budget


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'description', 'cost')
    list_filter = ('user',)


@admin.register(Profit)
class ProfitAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'amount', 'note')
    list_filter = ('user',)


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'period')
