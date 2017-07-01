from django.contrib import admin

from .models import Wallet, Budget, Transaction, BudgetCategory

admin.site.register(Wallet)
admin.site.register(BudgetCategory)
admin.site.register(Transaction)
admin.site.register(Budget)
