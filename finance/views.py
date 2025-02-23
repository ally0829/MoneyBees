from django.shortcuts import render
from .models import Expense, ExpenseCategory

# Create your views here.


def profile_view(request):
    return render(request, 'finance/profile.html', {"show_topbar": False})


def expense_record_view(request):
    categories = ExpenseCategory.objects.all()
    expenses = Expense.objects.all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = request.GET.get('category')

    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    if category and category != "ALL":
        expenses = expenses.filter(category__name=category)

    return render(request, 'finance/expenseRecord.html', {
        'categories': categories,
        'expenses': expenses,
    })
