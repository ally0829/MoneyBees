# signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
import requests
from django.conf import settings
from .models import Currency

@receiver(user_logged_in)
def update_currencies_on_login(sender, request, user, **kwargs):
    """
    Fetch and update currency data from the API when a user logs in.
    """
    api_key = settings.EXCHANGE_RATE_API_KEY
    url = f"http://api.exchangeratesapi.io/v1/latest?access_key={api_key}"

    # Make the API request
    response = requests.get(url)
    data = response.json()  # Convert JSON response to Python dictionary

    # Check if the request was successful
    if response.status_code == 200 and data.get("success", False):
        # Extract relevant data
        timestamp = data.get("timestamp")
        rates = data.get("rates", {})

        # Update or create Currency objects
        for currency_code, rate in rates.items():
            Currency.objects.update_or_create(
                currency=currency_code,
                defaults={
                    "rate": rate,
                    "timestamp": timestamp,
                }
            )
    else:
        # Handle API failure (e.g., log the error)
        print("Failed to fetch exchange rates.")