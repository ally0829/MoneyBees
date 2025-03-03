from django.shortcuts import render
<<<<<<< HEAD
import json
from django.shortcuts import render
from django.conf import settings
=======

from finance.forms import IncomeForm, ExpenseForm
from finance.models import Income, Expense, ExpenseCategory, MonthlyExpenseTarget, IncomeCategory, User

>>>>>>> 03032025

# Create your views here.
def profile_view(request):
    return render(request, 'finance/profile.html',{"show_topbar": False})

<<<<<<< HEAD
def settings_view(request):
     # Get the absolute path of the JSON file
    json_path = settings.DATA_DIR / 'currencies.json'

    # Load the JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        currencies = json.load(f)

    return render(request, 'finance/settings.html',{'currencies': currencies})
=======
def add_income(request):
    if request.method == 'POST':
        income_form = IncomeForm(request.POST)
        if income_form.is_valid():
            # Process the form data here
            print(income_form.cleaned_data)
            # get the income category from the form
            category = IncomeCategory.objects.get(name=income_form.cleaned_data['category'])
            income = Income(
                user=request.user,
                amount=income_form.cleaned_data['amount'],
                category=category,
                date=income_form.cleaned_data['date'],
                description=income_form.cleaned_data['description']
            )
            income.save()
    else:
        income_form = IncomeForm(initial={'user': request.user})
    return render(request, 'finance/add_expense_income.html', {
        "show_topbar": True, 
        "form": income_form,
        "type": "income"
    })

def add_expense(request):
    if request.method == 'POST':
        expense_form = ExpenseForm(request.POST)
        if expense_form.is_valid():
            # Process the form data here
            print(expense_form.cleaned_data)
            # get the category from the form
            category = ExpenseCategory.objects.get(name=expense_form.cleaned_data['category'])
            expense = Expense(
                user=request.user,
                amount=expense_form.cleaned_data['amount'],
                category=category,
                date=expense_form.cleaned_data['date'],
                description=expense_form.cleaned_data['description']
            )
            expense.save()
    else:
        expense_form = ExpenseForm(initial={'user': request.user})
    return render(request, 'finance/add_expense_income.html', {
        "show_topbar": True,
        "form": expense_form,
        "type": "expense"
    })
>>>>>>> 03032025
