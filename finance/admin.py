from django.contrib import admin
from .models import Income, ExpenseCategory, Expense, MonthlyExpenseTarget, IncomeCategory, UpcomingPayment


class IncomeCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Income)
admin.site.register(ExpenseCategory)
admin.site.register(Expense)
admin.site.register(MonthlyExpenseTarget)
admin.site.register(IncomeCategory, IncomeCategoryAdmin) 
admin.site.register(UpcomingPayment)
