from django.shortcuts import redirect, render, get_object_or_404
import json
from django.conf import settings
from finance.forms import IncomeForm, ExpenseForm
from finance.models import Income, Expense, ExpenseCategory, MonthlyExpenseTarget, IncomeCategory, User, UpcomingPayment
from django.db.models import Sum
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# Create your views here.


def home_view(request):
    return render(request, 'finance/homepage.html', {"show_topbar": True})


def profile_view(request):
    return render(request, 'finance/profile.html', {"show_topbar": False})


def settings_view(request):
    # Get the absolute path of the JSON file
    json_path = settings.DATA_DIR / 'currencies.json'

    # Load the JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        currencies = json.load(f)

    return render(request, 'finance/settings.html', {'currencies': currencies})


def faq_view(request):
    return render(request, 'finance/faq.html')


def add_income(request):
    if request.method == 'POST':
        income_form = IncomeForm(request.POST)
        if income_form.is_valid():
            # Process the form data here
            print(income_form.cleaned_data)
            # get the income category from the form
            category = IncomeCategory.objects.get(
                name=income_form.cleaned_data['category'])
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
            category = ExpenseCategory.objects.get(
                name=expense_form.cleaned_data['category'])
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
        "type": "expense"})


def edit_expense(request, expense_id):
    # Get the expense instance that we want to edit
    expense = get_object_or_404(Expense, id=expense_id)

    if request.method == 'POST':
        # If form was submitted, process the form
        expense_form = ExpenseForm(request.POST, instance=expense)
        if expense_form.is_valid():
            # Save the form but don't commit to the database yet
            updated_expense = expense_form.save(commit=False)
            # Make sure the user isn't changed
            updated_expense.user = expense.user
            # Now save to the database
            updated_expense.save()

            # Redirect to expense record page after successful update
            return redirect('finance:expense_record')

    else:
        # Initialize form with the expense instance and user
        expense_form = ExpenseForm(
            instance=expense,
            # This provides the user for the currency label
            initial={'user': expense.user}
        )

    return render(request, 'finance/add_expense_income.html', {
        "show_topbar": True,
        "form": expense_form,
        "type": "expense",
        "is_edit": True,  # Flag to indicate we're editing, not adding
        "expense_id": expense_id  # Pass the expense ID to the template
    })


def delete_expense(request, expense_id):
    # Get the expense instance that we want to delete
    expense = get_object_or_404(Expense, id=expense_id)

    if request.method == 'POST':
        # Delete the expense
        expense.delete()
        # Redirect to expense record page
        return redirect('finance:expense_record')

    # If it's a GET request, show confirmation page
    return render(request, 'finance/delete_expense_confirm.html', {
        'expense': expense,
        'show_topbar': True
    })


def expense_record_view(request):
    categories = ExpenseCategory.objects.all()
    expenses = Expense.objects.all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = request.GET.get('category')
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        start_date, end_date = None, None

    if start_date and end_date:
        expenses = expenses.filter(date__range=[start_date, end_date])
    elif start_date:
        expenses = expenses.filter(date__gte=start_date)
    elif end_date:
        expenses = expenses.filter(date__lte=end_date)

    if category and category != "ALL":
        expenses = expenses.filter(category__name=category)

    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'finance/expenseRecord.html', {
        'categories': categories,
        'expenses': expenses,
        'total_amount': total_amount,
        "show_topbar": True
    })

#  load Upcoming Expense page，including Category & Payments


@login_required
def upcomingExpense_view(request):
    categories = ExpenseCategory.objects.all()
    payments = UpcomingPayment.objects.filter(user=request.user)
    return render(request, 'finance/upcomingExpense.html', {
        "show_topbar": True,
        "categories": categories,
        "payments": payments
    })


#  API: new Upcoming Payment (front-end deliver AJAX use )
@csrf_exempt  # avoid CSRF token restrict
@login_required
def add_upcoming_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            category = get_object_or_404(ExpenseCategory, id=data["category"])
            payment = UpcomingPayment.objects.create(
                user=request.user,
                category=category,
                date=data["date"],
                amount=data["amount"],
                description=data["description"]
            )
            return JsonResponse({"message": "Payment added", "id": payment.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


#  API: edit Upcoming Payment
@csrf_exempt
@login_required
def edit_upcoming_payment(request, payment_id):
    if request.method == "POST":
        try:
            payment = get_object_or_404(
                UpcomingPayment, id=payment_id, user=request.user)
            data = json.loads(request.body)
            category = get_object_or_404(ExpenseCategory, id=data["category"])
            payment.category = category
            payment.date = data["date"]
            payment.amount = data["amount"]
            payment.description = data["description"]
            payment.save()
            return JsonResponse({"message": "Payment updated"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


#  API: delete Upcoming Payment
@csrf_exempt
@login_required
def delete_upcoming_payment(request, payment_id):
    try:
        payment = get_object_or_404(
            UpcomingPayment, id=payment_id, user=request.user)
        payment.delete()
        return JsonResponse({"message": "Payment deleted"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
