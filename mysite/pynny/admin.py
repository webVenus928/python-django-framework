from django.contrib import admin

from .models import Wallet, Budget, Transaction, BudgetCategory

class WalletAdmin(admin.ModelAdmin):
    '''Admin model for the Wallet object'''
    readonly_fields = ('created_time',)
    fieldsets = [
        (None, {'fields': ['user']}),
        ('Wallet Information', {'fields': ['name', 'balance', 'created_time']})
    ]


admin.site.register(Wallet, WalletAdmin)
admin.site.register(BudgetCategory)
admin.site.register(Transaction)
admin.site.register(Budget)
