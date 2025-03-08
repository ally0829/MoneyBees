from .models import ExchangeRate
from django.shortcuts import render
from users.models import Currency
import requests
from django.contrib.auth import update_session_auth_hash
from users.models import User
from django.shortcuts import redirect, render, get_object_or_404
import json
from django.conf import settings
from finance.forms import IncomeForm, ExpenseForm
from finance.models import Income, Expense, ExpenseCategory, MonthlyExpenseTarget, IncomeCategory, UpcomingPayment
from django.db.models import Sum
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils.timezone import now
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
logger = logging.getLogger(__name__)
# Create your views here.
# views.py
# Set up logging
# logger = logging.getLogger(__name__)
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum

def fetch_historic_exchange_rate(date, base_currency, target_currency):
    """
    Fetch the historic exchange rate for a specific date.
    """
    api_key = settings.EXCHANGE_RATE_API_KEY
    url = f"http://api.exchangeratesapi.io/v1/{date}?access_key={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        data = data.get("rates", {}).get(target_currency)

        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch exchange rates: {e}")
        return {}  # Return an empty dictionary in case of failure


def convert_to_default_currency(amount, expense_currency, default_currency, transaction_date):
    """
    Convert the given amount from expense_currency to default_currency
    using the historic exchange rate for the transaction date.
    """
    if expense_currency == default_currency:
        # No conversion needed
        return Decimal(amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Fetch the historic exchange rate
    exchange_rate = fetch_historic_exchange_rate(
        date=transaction_date,
        base_currency=default_currency,
        target_currency=expense_currency
    )

    if not exchange_rate:
        raise ValueError(f"Exchange rate not found for {expense_currency} on {transaction_date}.")

    # Convert the amount to the default currency
    converted_amount = Decimal(amount) / Decimal(exchange_rate)
    return converted_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calculate_total_amount(user, expenses):
    """
    Calculate the total amount of expenses in the user's default currency
    using historic exchange rates.
    """
    default_currency = user.currency.currency
    # total_amount = Decimal(0)
    total_amount = 0
    for expense in expenses:
        if not expense.currency:
            logger.error(f"Expense {expense.id} has no currency assigned.")
            continue  # Skip this expense or handle it appropriately

        # Convert each expense amount to the default currency
        converted_amount = convert_to_default_currency(
            amount=expense.amount,
            expense_currency=expense.currency.currency,  # Access currency code
            default_currency=default_currency,
            transaction_date=expense.date # Format date as YYYY-MM-DD
        )
        total_amount += converted_amount


    return total_amount

def fetch_exchange_rates():
    """
    Fetches the latest exchange rates from the API.
    Returns a dictionary containing the exchange rates and metadata.
    """
    api_key = settings.EXCHANGE_RATE_API_KEY
    url = f"http://api.exchangeratesapi.io/v1/latest?access_key={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        return {
            "success": data.get("success"),
            "timestamp": data.get("timestamp"),
            "base": data.get("base"),
            "date": data.get("date"),
            "rates": data.get("rates"),
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch exchange rates: {e}")
        return {}  # Return an empty dictionary in case of failure


@csrf_exempt
def toggle_notifications(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user  # Get the logged-in user
            # Update the ⁠ notification ⁠ field
            user.notification = data.get("enabled", False)
            user.save()  # Save the changes
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)


def get_exchange_rate(request):
    # Your API key (store it in settings.py for security)
    api_key = settings.EXCHANGE_RATE_API_KEY
    url = f"http://api.exchangeratesapi.io/v1/latest?access_key={api_key}"

    # Make the API request
    # Make the API request
    response = requests.get(url)
    # convert json to object
    response = response.json()
    print(response)
    items = response["Items"]
    print(items)

    json_itmes = []

    for item in items:
        currency = item["Item"]
        json_itmes.append({
            "success": currency["success"],
            "timestamp": currency["timestamp"],
            "base": currency["base"],
            "date": currency["date"],
            "rates": currency["rates"]
        })

    json_items = json.dump(json_items)

    return JsonResponse({"items": json_items}, status=200)


def home_view(request):
    return render(request, 'finance/homepage.html', {"show_topbar": True})


def profile_view(request):
    # Get the current user
    user = request.user
    return render(request, 'finance/profile.html', {
        "show_topbar": False,
        "notifications_enabled": user.notification,  # Pass the `notification` field
    })


def settings_view(request):
    # Fetch exchange rates using the utility function
    exchange_rates = fetch_exchange_rates()

    user = request.user

    # Handle form submission
    if request.method == 'POST':
        # Log form data
        logger.info("Form data submitted:")
        for key, value in request.POST.items():
            logger.info(f"{key}: {value}")

        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        selected_currency = request.POST.get('currency')

        # Update the User model
        if first_name:
            user.firstname = first_name  # Use `firstname` (not `first_name`)
        if last_name:
            user.lastname = last_name  # Use `lastname` (not `last_name`)
        if email:
            user.email = email
        if password:  # Update password if provided
            user.set_password(password)
            update_session_auth_hash(request, user)  # Keep the user logged in

        if selected_currency:
            try:
                # Get or create the Currency object
                currency, created = Currency.objects.get_or_create(
                    currency=selected_currency)
                # Update the rate and timestamp if the currency exists in the API response
                if exchange_rates.get("rates") and selected_currency in exchange_rates["rates"]:
                    currency.rate = exchange_rates["rates"][selected_currency]
                    currency.timestamp = exchange_rates.get(
                        "timestamp")  # Corrected timestamp assignment
                    currency.save()
                user.currency = currency  # Assign the Currency object
            except Exception as e:
                logger.error(f"Error updating currency: {e}")
                messages.error(
                    request, f"Invalid currency: {selected_currency}")

        user.save()
        # Debugging
        print(
            f"User {user.email} currency set to: {user.currency.currency} with rate: {user.currency.rate}")
        # Add a success message
        messages.success(request, "Settings updated successfully!")

        # Redirect to the same page to avoid form resubmission
        return redirect('finance:settings')

    # Pass the exchange_rates dictionary to the template
    context = {
        'exchange_rates': exchange_rates,
        'user': user
    }

    return render(request, 'finance/settings.html', context)


def faq_view(request):
    return render(request, 'finance/faq.html')


def add_income(request):
    exchange_rates = fetch_exchange_rates()

    if request.method == 'POST':
        print("POST data:", request.POST)

        income_form = IncomeForm(request.POST, initial={
                                 'user': request.user}, exchange_rates=exchange_rates)
        if income_form.is_valid():
            income = income_form.save(commit=False)
            income.user = request.user

            currency_code = request.POST.get('currency_display')

            try:
                currency, created = Currency.objects.get_or_create(
                    currency=currency_code)
                income.currency = currency
            except Exception as e:
                print(f"Currency error: {e}")
                income.currency = request.user.currency

            income.save()
            return redirect('finance:add_income')
        else:
            print("Form errors:", income_form.errors)
    else:
        income_form = IncomeForm(
            initial={'user': request.user}, exchange_rates=exchange_rates)

    return render(request, 'finance/add_expense_income.html', {
        "show_topbar": True,
        "form": income_form,
        "type": "income"
    })


def add_expense(request):
    # Fetch exchange rates using the utility function
    exchange_rates = fetch_exchange_rates()

    if request.method == 'POST':
        expense_form = ExpenseForm(request.POST, initial={
                                   'user': request.user}, exchange_rates=exchange_rates)
        if expense_form.is_valid():
            # Process the form data here
            print(expense_form.cleaned_data)
            # Get the category from the form
            category = ExpenseCategory.objects.get(
                name=expense_form.cleaned_data['category'])
            expense = Expense(
                user=request.user,
                amount=expense_form.cleaned_data['amount'],
                category=category,
                date=expense_form.cleaned_data['date'],
                description=expense_form.cleaned_data['description'],
                # Save the selected currency
                currency=Currency.objects.get(
                    currency=expense_form.cleaned_data['currency'])
            )
            expense.save()

            return redirect('finance:add_expense')
    else:
        # Remove the trailing comma here
        expense_form = ExpenseForm(
            initial={'user': request.user}, exchange_rates=exchange_rates)

    return render(request, 'finance/add_expense_income.html', {
        "show_topbar": True,
        "form": expense_form,
        "type": "expense"
    })


def edit_expense(request, expense_id):
    api_key = settings.EXCHANGE_RATE_API_KEY
    url = f"http://api.exchangeratesapi.io/v1/latest?access_key={api_key}"
    # Make the API request
    response = requests.get(url)
    data = response.json()  # Convert JSON response to Python dictionary

    user = request.user

    if response.status_code == 200:
        # Extract relevant data
        exchange_rates = {
            "success": data.get("success"),
            "timestamp": data.get("timestamp"),
            "base": data.get("base"),
            "date": data.get("date"),
            "rates": data.get("rates"),
        }
    else:
        exchange_rates = {}  # Fallback in case of API failure

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
        "expense_id": expense_id,  # Pass the expense ID to the template,
        "currency": exchange_rates
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
    user = request.user

    # Ensure user has a valid currency


    categories = ExpenseCategory.objects.all()
    expenses = Expense.objects.filter(user=user)
    # expenses = Expense.objects.filter(user=user)

    total_amount = calculate_total_amount(user, expenses)

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
        expenses = expenses.filter(date__lte=end_date) * user.currency.rate

    if category and category != "ALL":
        expenses = expenses.filter(category__name=category)

    # total_amount = expenses.aggregate(
    #     Sum('amount'))['amount__sum']

    return render(request, 'finance/expenseRecord.html', {
        'categories': categories,
        'expenses': expenses,
        'total_amount': total_amount,
        "show_topbar": True,
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


def mark_payment_paid(request, payment_id):
    if request.method == 'POST':
        # Get the upcoming payment
        payment = get_object_or_404(UpcomingPayment, id=payment_id)

        # Create a new expense record from this payment
        expense = Expense(
            user=payment.user,
            category=payment.category,
            amount=payment.amount,
            date=datetime.now().date(),
            description=f"{payment.description}"
        )
        expense.save()

        # Delete the upcoming payment
        payment.delete()

        return JsonResponse({'message': 'Payment marked as paid and added to expenses'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

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


def test_email(request):
    user_email = request.user.email if request.user.is_authenticated else "test@example.com"

    try:
        send_mail(
            subject="Test Email from MoneyBees",
            message="This is a test email from your MoneyBees application.",
            from_email="MoneyBees <alice850829@gmail.com>",
            recipient_list=[user_email],
            fail_silently=False,
        )
        return HttpResponse("Test email has been sent to your email address!")
    except Exception as e:
        return HttpResponse(f"Error sending email: {str(e)}")
# API: return the percentage of the expense per month in the home page


@login_required
def spending_summary(request):

    user = request.user
    today = now().date()

    current_year = today.year
    current_month = today.month

    expenses = Expense.objects.filter(
        user=user,
        date__year=current_year,
        date__month=current_month
    )
    result = expenses.aggregate(total=Sum('amount'))
    total_spent = result.get('total', 0)

    category_data = expenses.values(
        'category__id', 'category__name').annotate(total=Sum('amount'))

    data = [
        {
            "category_id": category['category__id'],
            "category": category['category__name'],
            "amount": category['total'],
            "percentage": round((category['total']/total_spent)*100, 2) if total_spent > 0 else 0

        }
        for category in category_data
    ]
    print(f"🟢 {current_year}-{current_month} expense data:", data)

    return JsonResponse({"total_spent": total_spent, "categories": data})


@login_required
def upcoming_expenses(request):

    user = request.user
    today = now().date()

    upcoming_payments = UpcomingPayment.objects.filter(
        user=user, date__gte=today).order_by('date')[:3]

    data = [
        {
            "category": payment.category.name,
            "amount": payment.amount,
            "due_date": payment.date.strftime("%d %b")
        }
        for payment in upcoming_payments
    ]

    return JsonResponse({"upcoming_expenses": data})


@csrf_exempt
@login_required
def expense_targets(request):
    user = request.user
    today = now().date()
    current_year = today.year
    current_month = today.month

    if request.method == "GET":
        category_id = request.GET.get("category_id")

        if category_id:
            try:
                category_id = int(category_id)
            except ValueError:
                return JsonResponse({"error": "Invalid category_id"}, status=400)

            target = MonthlyExpenseTarget.objects.filter(
                user=user, category_id=category_id, month=current_month
            ).first()

            if target:
                return JsonResponse({
                    "id": target.id,
                    "category": target.category.name,
                    "target_amount": float(target.amount),
                    "month": target.month,
                })
            else:
                return JsonResponse({"message": "No target found"}, status=404)

        targets = MonthlyExpenseTarget.objects.filter(
            user=user, month=current_month)
        expenses = Expense.objects.filter(user=user, date__year=current_year, date__month=current_month).values(
            'category').annotate(total=Sum('amount'))
        expense_dict = {expense['category']: expense['total']
                        for expense in expenses}

        data = [
            {
                "category": target.category.name,
                "target_amount": float(target.amount),
                "current_spent": float(expense_dict.get(target.category.id, 0)),
                "progress": round((expense_dict.get(target.category.id, 0) / target.amount) * 100, 2) if target.amount > 0 else 0
            }
            for target in targets
        ]

        return JsonResponse({"expense_targets": data})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            category_id = int(data.get("category"))
            amount = float(data.get("amount"))
            month_str = data.get("month")

            category = get_object_or_404(ExpenseCategory, id=category_id)

            try:
                month = int(month_str.split("-")[1])
            except (IndexError, ValueError):
                return JsonResponse({"error": "Invalid month format. Expected YYYY-MM."}, status=400)

            print(
                f"try to create MonthlyExpenseTarget: User={user.email}, Category={category.name}, Amount={amount}, Month={month}")

            target = MonthlyExpenseTarget.objects.create(
                user=user,
                category=category,
                amount=amount,
                month=month
            )

            print(f"Success: {target}")

            return JsonResponse({"message": "Success", "id": target.id}, status=201)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@login_required
def update_expense_target(request, target_id):
    try:
        print(f"🔍 Debug: Received target_id = {target_id}")

        target = get_object_or_404(
            MonthlyExpenseTarget, id=target_id, user=request.user)
        print(f"Found target: {target}")

        if request.method == "PUT":
            data = json.loads(request.body)
            amount = data.get("amount")

            if not amount:
                return JsonResponse({"error": "Amount is required"}, status=400)

            target.amount = float(amount)
            target.save()

            print(f"Successfully updated: {target.amount}")
            return JsonResponse({"message": "Updated successfully", "id": target.id}, status=200)

    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def categories(request):
    print(f"User {request.user} requested categories")
    categories = ExpenseCategory.objects.values("id", "name")
    return JsonResponse({"categories": list(categories)})


@login_required
def get_current_user(request):
    return JsonResponse({
        "user_id": request.user.id,
        "username": getattr(request.user, "username", request.user.email)
    })


@login_required
def yearly_summary(request):
    """
    Returns monthly income and expense summaries for the current year
    """
    user = request.user
    today = now().date()
    current_year = today.year

    # Initialize result data structure
    monthly_data = []
    for month in range(1, 13):
        monthly_data.append({
            "month": month,
            # Month abbreviation (Jan, Feb, etc.)
            "month_name": datetime(current_year, month, 1).strftime('%b'),
            "income": 0,
            "expenses": 0
        })

    # Get income data for each month in current year
    incomes = Income.objects.filter(
        user=user,
        date__year=current_year
    ).values('date__month').annotate(total=Sum('amount'))

    # Populate income data
    for income in incomes:
        month_idx = income['date__month'] - 1  # Convert to 0-based index
        monthly_data[month_idx]['income'] = float(income['total'])

    # Get expense data for each month in current year
    expenses = Expense.objects.filter(
        user=user,
        date__year=current_year
    ).values('date__month').annotate(total=Sum('amount'))

    # Populate expense data
    for expense in expenses:
        month_idx = expense['date__month'] - 1  # Convert to 0-based index
        monthly_data[month_idx]['expenses'] = float(expense['total'])

    # Calculate yearly totals
    yearly_totals = {
        "total_income": sum(item['income'] for item in monthly_data),
        "total_expenses": sum(item['expenses'] for item in monthly_data)
    }

    return JsonResponse({
        "monthly_data": monthly_data,
        "yearly_totals": yearly_totals
    })
