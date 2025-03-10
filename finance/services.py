
import requests
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import logging
from django.conf import settings


def fetch_historic_exchange_rate(date, base_currency, target_currency):
    """
    Fetch the exchange rate for a specific date.
    Always uses EUR as the base currency.
    """
    print(f"Base Currency: {base_currency}, Date: {date}, Target Currency: {target_currency}")

    # Check if the date is in the future
    if datetime.strptime(date, "%Y-%m-%d").date() > datetime.now().date():
        logger.warning(f"Future date {date} is not supported. Using latest exchange rate.")
        date = "latest"  # Use the latest exchange rate for future dates

    api_key = settings.EXCHANGE_RATE_API_KEY
    url = f"https://api.exchangeratesapi.io/v1/{date}?access_key={api_key}&base=EUR&symbols={base_currency},{target_currency}"

    print(f"API URL: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        print(f"API Response: {data}")

        if not data.get("success", False):
            error_message = data.get("error", {}).get("info", "Unknown error")
            logger.error(f"API error: {error_message}")
            return None

        # Extract the exchange rates
        rates = data.get("rates", {})
        base_rate = rates.get(base_currency)
        target_rate = rates.get(target_currency)

        if not base_rate or not target_rate:
            logger.error(f"Exchange rates not found for {base_currency} or {target_currency} on {date}.")
            return None

        # Calculate the exchange rate from base_currency to target_currency
        exchange_rate = target_rate / base_rate
        return Decimal(str(exchange_rate))
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch exchange rates: {e}")
        return None


def convert_to_default_currency(amount, expense_currency, default_currency, transaction_date):
    """
    Convert the given amount from expense_currency to default_currency
    using the historic exchange rate for the transaction date.
    """
    if expense_currency == default_currency:
        # No conversion needed
        return Decimal(amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Fetch the exchange rate from expense_currency to default_currency
    exchange_rate = fetch_historic_exchange_rate(
        date=transaction_date.strftime("%Y-%m-%d"),  # Format date as YYYY-MM-DD
        base_currency=expense_currency,
        target_currency=default_currency
    )

    if not exchange_rate:
        raise ValueError(f"Exchange rate not found for {expense_currency} to {default_currency} on {transaction_date}.")

    # Convert the amount to the default currency
    converted_amount = Decimal(amount) * exchange_rate
    return converted_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calculate_total_amount(user, expenses):
    """
    Calculate the total amount of expenses in the user's default currency
    using historic exchange rates.
    """
    default_currency = user.currency.currency
    total_amount = Decimal(0)

    for expense in expenses:
        if not expense.currency:
            logger.warning(f"Expense {expense.id} has no currency assigned.")
            continue  # Skip this expense or handle it appropriately

        # Convert each expense amount to the default currency
        converted_amount = convert_to_default_currency(
            amount=expense.amount,
            expense_currency=expense.currency.currency,  # Access currency code
            default_currency=default_currency,
            transaction_date=expense.date  # Format date as YYYY-MM-DD
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