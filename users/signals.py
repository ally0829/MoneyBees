# signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
import requests
from django.conf import settings
from .models import Currency
from django.db.models.signals import post_save
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=SocialAccount)
def update_user_profile(sender, instance, created, **kwargs):
    """
    This signal ensures that when a user signs in via Google, 
    their first name and last name are stored in the User model.
    """
    if created:  # Only run when the account is first created
        user = instance.user
        google_data = instance.extra_data  # Google API Data
        print("Google extra_data:", google_data)
        user.firstname = google_data.get('given_name', user.firstname or "Google User")
        user.lastname = google_data.get('family_name', user.lastname or "*")
        user.is_staff = True
        # print(f"Updating user: {user.email}, is_staff={user.is_staff}, firstname={user.firstname}, lastname={user.lastname}")
        user.save()


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