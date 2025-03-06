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
# from users.models import Currency
logger = logging.getLogger(__name__)
# Create your views here.


# views.py
import requests
from django.http import JsonResponse
from django.conf import settings

def get_exchange_rate(request):
    # Your API key (store it in settings.py for security)
    api_key = settings.EXCHANGE_RATE_API_KEY
    url = f"http://api.exchangeratesapi.io/v1/latest?access_key={api_key}"

    # Make the API request
        # Make the API request
    response = requests.get(url)
        #convert json to object
    response = response.json()
    print(response)
    items=response["Items"]
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



# finance/views.py
from django.shortcuts import render
from .models import ExchangeRate
from .utils import fetch_exchange_rates

def currency_converter(request):
    usd_to_eur = ExchangeRate.objects.get(base_currency='USD', target_currency='EUR').rate
    context = {'usd_to_eur': usd_to_eur}
    return render(request, 'converter.html', context)

def home_view(request):
    return render(request, 'finance/homepage.html', {"show_topbar": True})

def profile_view(request):
    return render(request, 'finance/profile.html', {"show_topbar": False})


# def settings_view(request):
#     api_key = settings.EXCHANGE_RATE_API_KEY
#     url = f"http://api.exchangeratesapi.io/v1/latest?access_key={api_key}"

#     exchange_rates = ExchangeRate.objects.all()

#     context = {
#         'exchange_rates': exchange_rates,
#     }

#     # Make the API request
#     response = requests.get(url)
#         #convert json to object
#     response = response.json()
#     print(response)
#     # items=response[0]
#     # print(items)
    
#     json_items = []

#     for item in response:
#         currency =  item
#         json_items.append({
#             "success": currency["success"],
#             "timestamp": currency["timestamp"],
#             "base": currency["base"],
#             "date": currency["date"],
#             "rates": currency["rates"]
#         })
#     #serialize item to json
#     # json_items = json.dump(json_items)

#     # Check if the request was successful
#     if response.status_code == 200:
#         currencies = response.json()

#     # if request.method == 'POST':
#     #     # Handle form submission
#     #     user = request.user
#     #     full_name = request.POST.get('full_name', '')  # Get full name from form

#     #     # Split full name into first and last name
#     #     name_parts = full_name.strip().split(maxsplit=1)  # Split into two parts
#     #     first_name = name_parts[0] if len(name_parts) > 0 else ''
#     #     last_name = name_parts[1] if len(name_parts) > 1 else ''
#     #     email = request.POST.get('email')
#     #     password = request.POST.get('password')
#     #     currency_code = request.POST.get('currency')

#     #     # Update user information
#     #     if first_name:
#     #         user.first_name = first_name
#     #     if last_name:
#     #         user.last_name = last_name 
#     #     if email:
#     #         user.email = email
#     #     if password:
#     #         user.set_password(password)  # Set password securely

#     #     # Update currency
#     #     try:
#     #         selected_currency = Currency.objects.get(code=currency_code)
#     #         user.currency = selected_currency
#     #     except Currency.DoesNotExist:
#     #         pass  # If currency doesn't exist, we don't change it

#     #     user.save()
#     #     return redirect('finance:settings')  # Redirect to the same settings page after saving
#     # # Get the absolute path of the JSON file

#     # # Get the current user's currency
#     # current_currency = request.user.currency if request.user.currency else None

    

#     return render(request, 'finance/settings.html', {
#         'currencies': currencies,
#         # 'current_currency': current_currency,
#         'items': json_items,
#     })
def settings_view(request):
    api_key = settings.EXCHANGE_RATE_API_KEY
    url = f"http://api.exchangeratesapi.io/v1/latest?access_key=db182e54f6c67865d0a9db5ebe11036b"

    # Make the API request
    response = requests.get(url)
    data = response.json()  # Convert JSON response to Python dictionary
    print(data)  # Debugging: Print the response data

    # Check if the request was successful
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

    # Fetch existing exchange rates from the database (if needed)
    exchange_rates_db = ExchangeRate.objects.all()

    # Prepare the context
    context = {
        'exchange_rates': exchange_rates,
        'exchange_rates_db': exchange_rates_db,
        'items': exchange_rates,  # Pass the exchange_rates data as 'items'
    }

    return render(request, 'finance/settings.html', context)

# def settings_view(request):
#     user = request.user  # Get the logged-in user

#     if request.method == 'POST':
#         user_form = SettingsForm(request.POST, instance=user)  # Bind form to existing user
#         if user_form.is_valid():
#             user_form.save()  # Saves the user details

#             messages.success(request, "Settings updated successfully!")
#             return redirect('finance:settings')  # Redirect to prevent re-submission

#     else:
#         user_form = SettingsForm(instance=user)  # Pre-fill form with existing user details

#     # Load the available currencies from a JSON file
#     json_path = settings.DATA_DIR / 'currencies.json'
#     with open(json_path, 'r', encoding='utf-8') as f:
#         currencies = json.load(f)

#     # Get the current user's currency
#     current_currency = user.currency if user.currency else None

#     return render(request, 'finance/settings.html', {
#         'form': user_form,  # Pass the form to the template
#         'currencies': currencies,
#         'current_currency': current_currency
#     })


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

    user=request.user
    today=now().date()
    first_day_of_month=today.replace(day=1)

    expenses=Expense.objects.filter(user=user,date__gte=first_day_of_month)
    result = expenses.aggregate(total=Sum('amount'))
    total_spent = result.get('total', 0)  


    category_data=expenses.values('category__name').annotate(total=Sum('amount'))

    data=[
        {
            "category":category['category__name'],
            "amount":category['total'],
            "percentage":round((category['total']/total_spent)*100,2) if total_spent>0 else 0 

        }
        for category in category_data
    ]

    return JsonResponse({"total_spent": total_spent,"categories":data})

@login_required
def upcoming_expenses(request):
    
    user=request.user
    today=now().date()

    upcoming_payments=UpcomingPayment.objects.filter(user=user,date__gte=today).order_by('date')[:3]

    data=[
        {
           "category":payment.category.name,
           "amount":payment.amount,
           "due_date":payment.date.strftime("%d %b")
        }
        for payment in upcoming_payments
    ]

    return JsonResponse({"upcoming_expenses":data})

@csrf_exempt
@login_required
def expense_targets(request):
    user = request.user
    today = now().date()
    first_day_of_month = today.replace(day=1)

    if request.method == "GET":
        targets = MonthlyExpenseTarget.objects.filter(user=user)
        expenses = Expense.objects.filter(user=user, date__gte=first_day_of_month).values('category').annotate(total=Sum('amount'))

        expense_dict = {expense['category']: expense['total'] for expense in expenses}

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
            category_id = data.get("category")
            amount = data.get("amount")
            month_str = data.get("month")  

            category = get_object_or_404(ExpenseCategory, id=category_id)

            try:
                month = int(month_str.split("-")[1]) 
            except (IndexError, ValueError):
                return JsonResponse({"error": "Invalid month format. Expected YYYY-MM."}, status=400)

            print(f"try to create MonthlyExpenseTarget: User={user.email}, Category={category.name}, Amount={amount}, Month={month}")

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
