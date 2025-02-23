from django.shortcuts import render
from .models import Expense, ExpenseCategory
from django.db.models import Sum
from datetime import datetime

# Create your views here.


def profile_view(request):
    return render(request, 'finance/profile.html', {"show_topbar": False})


def expense_record_view(request):
    categories = ExpenseCategory.objects.all()
    expenses = Expense.objects.all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = request.GET.get('category')

    # 確保日期格式正確
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        start_date, end_date = None, None

    # 過濾日期範圍內的資料
    if start_date and end_date:
        expenses = expenses.filter(date__range=[start_date, end_date])
    elif start_date:
        expenses = expenses.filter(date__gte=start_date)
    elif end_date:
        expenses = expenses.filter(date__lte=end_date)

    # 過濾類別
    if category and category != "ALL":
        expenses = expenses.filter(category__name=category)

    # 計算總金額
    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'finance/expenseRecord.html', {
        'categories': categories,
        'expenses': expenses,
        'total_amount': total_amount,
    })
