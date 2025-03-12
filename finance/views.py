from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.db.models import Sum
from django.db import models
from decimal import Decimal
from datetime import datetime
import json
import logging

from users.models import User, Currency
from finance.forms import IncomeForm, ExpenseForm
from finance.models import (
    Income, Expense, ExpenseCategory, MonthlyExpenseTarget,
    IncomeCategory, UpcomingPayment
)
from .services import convert_to_default_currency, calculate_total_amount, fetch_exchange_rates

logger = logging.getLogger(__name__)


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


@login_required
def home_view(request):
    # Example: Fetch data for the charts
    # categories = ExpenseCategory.objects.all()
    expenses = Expense.objects.filter(user=request.user)
    # total_spent = calculate_total_amount(request.user, expenses)

    # Pass data to the template
    return render(request, 'finance/homepage.html', {
        "show_topbar": True,
        # "categories": categories,
        # "total_spent": total_spent,
    })


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
        # print("POST data:", request.POST)

        income_form = IncomeForm(request.POST, initial={
                                 'user': request.user}, exchange_rates=exchange_rates)
        if income_form.is_valid():
            category = IncomeCategory.objects.get(
                name=income_form.cleaned_data['category'])
            income = Income(
                user=request.user,
                amount=income_form.cleaned_data['amount'],
                category=category,
                date=income_form.cleaned_data['date'],
                description=income_form.cleaned_data['description'],
                # Save the selected currency
                currency=Currency.objects.get(
                    currency=income_form.cleaned_data['currency'])
            )
            # income = income_form.save(commit=False)
            # income.user = request.user

            # currency_code = request.POST.get('currency_display')

            # try:
            #     currency, created = Currency.objects.get_or_create(
            #         currency=currency_code)
            #     income.currency = currency
            # except Exception as e:
            #     print(f"Currency error: {e}")
            #     income.currency = request.user.currency

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
    exchange_rates = fetch_exchange_rates()

    # Get the expense instance that we want to edit
    expense = get_object_or_404(Expense, id=expense_id)

    if request.method == 'POST':
        # If form was submitted, process the form
        expense_form = ExpenseForm(
            request.POST, instance=expense, exchange_rates=exchange_rates)
        if expense_form.is_valid():
            # Save the form but don't commit to the database yet
            updated_expense = expense_form.save(commit=False)
            # Make sure the user isn't changed
            updated_expense.user = expense.user

            # Handle currency if provided in POST data
            currency_code = request.POST.get('currency_display')
            if currency_code:
                currency, created = Currency.objects.get_or_create(
                    currency=currency_code)
                updated_expense.currency = currency

            # Now save to the database
            updated_expense.save()

            # Redirect to expense record page after successful update
            return redirect('finance:expense_record')

    else:
        # Initialize form with the expense instance and user
        expense_form = ExpenseForm(
            instance=expense,
            # This provides the user for the currency label
            initial={'user': expense.user},
            # Pass exchange rates to the form
            exchange_rates=exchange_rates
        )

    return render(request, 'finance/add_expense_income.html', {
        "show_topbar": True,
        "form": expense_form,
        "type": "expense",
        "is_edit": True,  # Flag to indicate we're editing, not adding
        "expense_id": expense_id  # Pass the expense ID to the template
    })


def edit_income(request, income_id):
    exchange_rates = fetch_exchange_rates()

    # Get the income instance that we want to edit
    income = get_object_or_404(Income, id=income_id)

    if request.method == 'POST':
        # If form was submitted, process the form
        income_form = IncomeForm(
            request.POST, instance=income, exchange_rates=exchange_rates)
        if income_form.is_valid():
            # Save the form but don't commit to the database yet
            updated_income = income_form.save(commit=False)
            # Make sure the user isn't changed
            updated_income.user = income.user

            # Handle currency if provided in POST data
            currency_code = request.POST.get('currency_display')
            if currency_code:
                currency, created = Currency.objects.get_or_create(
                    currency=currency_code)
                updated_income.currency = currency

            # Now save to the database
            updated_income.save()

            # Redirect to income record page after successful update
            return redirect('finance:income_record')

    else:
        # Initialize form with the income instance and user
        income_form = IncomeForm(
            instance=income,
            # This provides the user for the currency label
            initial={'user': income.user},
            # Pass exchange rates to the form
            exchange_rates=exchange_rates
        )

    return render(request, 'finance/add_expense_income.html', {
        "show_topbar": True,
        "form": income_form,
        "type": "income",
        "is_edit": True,  # Flag to indicate we're editing, not adding
        "income_id": income_id  # Pass the income ID to the template
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


def delete_income(request, income_id):
    # Get the expense instance that we want to delete
    income = get_object_or_404(Income, id=income_id)

    if request.method == 'POST':
        # Delete the expense
        income.delete()
        # Redirect to expense record page
        return redirect('finance:income_record')

    # If it's a GET request, show confirmation page
    return render(request, 'finance/delete_income_confirm.html', {
        'income': income,
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


def income_record_view(request):
    user = request.user

    categories = IncomeCategory.objects.all()
    incomes = Income.objects.all()

    total_amount = calculate_total_amount(user, incomes)

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
        incomes = incomes.filter(date__range=[start_date, end_date])
    elif start_date:
        incomes = incomes.filter(date__gte=start_date)
    elif end_date:
        incomes = incomes.filter(date__lte=end_date) * user.currency.rate

    if category and category != "ALL":
        incomes = incomes.filter(category__name=category)

    return render(request, 'finance/incomeRecord.html', {
        'categories': categories,
        'incomes': incomes,
        'total_amount': total_amount,
        "show_topbar": True,
    })

#  load Upcoming Expense page，including Category & Payments


@login_required
def upcomingExpense_view(request):
    # Fetch exchange rates using the utility function
    exchange_rates = fetch_exchange_rates()

    categories = ExpenseCategory.objects.all()
    payments = UpcomingPayment.objects.filter(user=request.user)

    return render(request, 'finance/upcomingExpense.html', {
        "show_topbar": True,
        "categories": categories,
        "payments": payments,
        "exchange_rates": exchange_rates  # Pass exchange rates to the template
    })


#  API: new Upcoming Payment (front-end deliver AJAX use )
@csrf_exempt
@login_required
def add_upcoming_payment(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            print("Received data:", data)  # Debug: Print the received data

            # Validate required fields
            required_fields = ["category", "date",
                               "amount", "description", "currency"]
            for field in required_fields:
                if field not in data:
                    return JsonResponse({"error": f"Missing required field: {field}"}, status=400)

            # Fetch the category
            category = get_object_or_404(ExpenseCategory, id=data["category"])

            # Fetch the selected currency from the request data
            currency_code = data.get("currency")
            if not currency_code:
                return JsonResponse({"error": "Currency is required"}, status=400)

            # Fetch exchange rates from the API
            exchange_rates = fetch_exchange_rates()
            if not exchange_rates.get("success"):
                return JsonResponse({"error": "Failed to fetch exchange rates"}, status=400)

            # Check if the selected currency exists in the API response
            rates = exchange_rates.get("rates", {})
            if currency_code not in rates:
                return JsonResponse({"error": f"Currency {currency_code} not found in API response"}, status=400)

            # Get or create the Currency object
            currency, created = Currency.objects.get_or_create(
                currency=currency_code,
                defaults={
                    "rate": rates[currency_code],  # Use the rate from the API
                    # Use the timestamp from the API
                    "timestamp": exchange_rates.get("timestamp")
                }
            )

            # Create the upcoming payment
            payment = UpcomingPayment.objects.create(
                user=request.user,
                category=category,
                date=data["date"],
                amount=data["amount"],
                description=data["description"],
                currency=currency  # Assign the fetched or created Currency object
            )

            return JsonResponse({"message": "Payment added", "id": payment.id})
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
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
            # Default to USD if not provided
            currency_code = data.get("currency", "USD")

            # Get or create the Currency object
            currency, created = Currency.objects.get_or_create(
                currency=currency_code,
                # Default values for new objects
                defaults={"rate": 1.0, "timestamp": 1698765432}
            )

            payment.category = category
            payment.date = data["date"]
            payment.amount = data["amount"]
            payment.description = data["description"]
            payment.currency = currency  # Update the Currency object
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

    # Fetch expenses for the current month
    expenses = Expense.objects.filter(
        user=user,
        date__year=current_year,
        date__month=current_month
    )

    # Calculate the total amount in the user's default currency
    total_spent = calculate_total_amount(user, expenses)

    # Group expenses by category and calculate totals in the user's default currency
    category_data = []
    for expense in expenses:
        if not expense.currency:
            logger.error(f"Expense {expense.id} has no currency assigned.")
            continue  # Skip this expense or handle it appropriately

        # Convert the expense amount to the user's default currency
        converted_amount = convert_to_default_currency(
            amount=expense.amount,
            expense_currency=expense.currency.currency,
            default_currency=user.currency.currency,
            transaction_date=expense.date
        )

        # Find or create the category in the category_data list
        category_found = False
        for category in category_data:
            if category['category_id'] == expense.category.id:
                category['total'] += converted_amount
                category_found = True
                break

        if not category_found:
            category_data.append({
                "category_id": expense.category.id,
                "category": expense.category.name,
                "total": converted_amount
            })

    # Calculate percentages for each category
    data = [
        {
            "category_id": category['category_id'],
            "category": category['category'],
            # Convert Decimal to float for JSON serialization
            "amount": float(category['total']),
            "percentage": round((category['total'] / total_spent) * 100, 2) if total_spent > 0 else 0
        }
        for category in category_data
    ]

    # Debug the data
    print(f"🟢 {current_year}-{current_month} expense data:", data)

    # Return the JSON response
    return JsonResponse({
        # Convert Decimal to float for JSON serialization
        "total_spent": float(total_spent),
        # Include the currency symbol (e.g., AED, USD)
        "currency_symbol": user.currency.currency,
        "categories": data
    })


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
            "due_date": payment.date.strftime("%d %b"),
            "currency": payment.currency.currency
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
                    "currency": user.currency.currency  # Include currency in response

                })
            else:
                return JsonResponse({"message": "No target found"}, status=404)
        # Fetch all targets for the current month
        targets = MonthlyExpenseTarget.objects.filter(
            user=user, month=current_month)
        # Fetch expenses for the current month and group by category
        expenses = Expense.objects.filter(user=user, date__year=current_year, date__month=current_month).values(
            'category').annotate(total=Sum('amount'))
        expense_dict = {expense['category']: expense['total']
                        for expense in expenses}

        # data = [
        #     {
        #         "category": target.category.name,
        #         "target_amount": float(target.amount),
        #         "current_spent": float(expense_dict.get(target.category.id, 0)),
        #         "progress": round((expense_dict.get(target.category.id, 0) / target.amount) * 100, 2) if target.amount > 0 else 0,
        #         "currency": user.currency.currency
        #     }
        #     for target in targets
        # ]
        # Prepare data for JSON response
        data = []
        for target in targets:
            # Convert target amount to the user's default currency
            target_amount = Decimal(target.amount)

            # Get the current spending for the category
            current_spent = Decimal(expense_dict.get(target.category.id, 0))

            # Convert current spending to the user's default currency
            for expense in Expense.objects.filter(user=user, category=target.category, date__year=current_year, date__month=current_month):
                converted_amount = convert_to_default_currency(
                    amount=expense.amount,
                    expense_currency=expense.currency.currency,
                    default_currency=user.currency.currency,
                    transaction_date=expense.date
                )
                current_spent += converted_amount
                target_amount += converted_amount

            # Calculate progress percentage
            progress = round((current_spent / target_amount) * 100, 2) if target_amount > 0 else 0

            data.append({
                "category": target.category.name,
                "target_amount": float(target_amount),  # Convert Decimal to float for JSON
                "current_spent": float(current_spent),  # Convert Decimal to float for JSON
                "progress": progress,
                "currency": user.currency.currency  # Include currency in response
            })

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
    Returns monthly income and expense summaries for the current year,
    with all amounts converted to the user's default currency.
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
            "income": Decimal(0),  # Use Decimal for precision
            "expenses": Decimal(0)  # Use Decimal for precision
        })

    # Get income data for each month in the current year
    incomes = Income.objects.filter(
        user=user,
        date__year=current_year
    )

    # Convert income amounts to the user's default currency
    for income in incomes:
        if not income.currency:
            logger.error(f"Income {income.id} has no currency assigned.")
            continue  # Skip this income or handle it appropriately

        # Convert the income amount to the user's default currency
        converted_amount = convert_to_default_currency(
            amount=income.amount,
            expense_currency=income.currency.currency,
            default_currency=user.currency.currency,
            transaction_date=income.date
        )

        # Add the converted amount to the corresponding month
        month_idx = income.date.month - 1  # Convert to 0-based index
        monthly_data[month_idx]['income'] += converted_amount

    # Get expense data for each month in the current year
    expenses = Expense.objects.filter(
        user=user,
        date__year=current_year
    )

    # Convert expense amounts to the user's default currency
    for expense in expenses:
        if not expense.currency:
            logger.error(f"Expense {expense.id} has no currency assigned.")
            continue  # Skip this expense or handle it appropriately

        # Convert the expense amount to the user's default currency
        converted_amount = convert_to_default_currency(
            amount=expense.amount,
            expense_currency=expense.currency.currency,
            default_currency=user.currency.currency,
            transaction_date=expense.date
        )

        # Add the converted amount to the corresponding month
        month_idx = expense.date.month - 1  # Convert to 0-based index
        monthly_data[month_idx]['expenses'] += converted_amount

    # Calculate yearly totals
    yearly_totals = {
        "total_income": sum(item['income'] for item in monthly_data),
        "total_expenses": sum(item['expenses'] for item in monthly_data)
    }

    # Convert Decimal values to float for JSON serialization
    for item in monthly_data:
        item['income'] = float(item['income'])
        item['expenses'] = float(item['expenses'])

    yearly_totals['total_income'] = float(yearly_totals['total_income'])
    yearly_totals['total_expenses'] = float(yearly_totals['total_expenses'])

    # Return the JSON response
    return JsonResponse({
        "monthly_data": monthly_data,
        "yearly_totals": yearly_totals
    })

@login_required
@require_POST  # Ensure this view only accepts POST requests
def delete_account(request):
    # Delete the user's account
    user = request.user
    user.delete()

    # Log the user out
    logout(request)

    # Redirect to the login page
    return redirect('login') 