from django.contrib import admin
from .models import Income, ExpenseCategory, Expense, MonthlyExpenseTarget , UpcomingPayment

# Register your models here.

admin.site.register(Income)
admin.site.register(ExpenseCategory)
admin.site.register(Expense)
admin.site.register(MonthlyExpenseTarget)
admin.site.register(UpcomingPayment)
