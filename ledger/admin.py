from django.contrib import admin
from .models import Entry, Profit, Budget


class EntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'description', 'cost')
    list_filter = ('user',)


class ProfitAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'amount', 'note')
    list_filter = ('user',)


class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'period')


admin.site.register(Entry, EntryAdmin)
admin.site.register(Profit, ProfitAdmin)
admin.site.register(Budget, BudgetAdmin)
