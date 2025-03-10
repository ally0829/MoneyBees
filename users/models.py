from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import requests

class CustomUserManager(BaseUserManager):
    def create_user(self, email, firstname, lastname, password=None):
        """Create and return a regular user with email and password."""
        if not email:
            raise ValueError("Users must have an email address")

        # Normalize the email address
        email = self.normalize_email(email)
        user = self.model(email=self.normalize_email(email),
                          firstname=firstname, lastname=lastname)


        # Create the user
        user = self.model(
            email=email,
            firstname=firstname,
            lastname=lastname,
        )
        user.set_password(password)
        user.is_active = True

        # Ensure the user has a default currency (GBP)
        if not user.currency:
            user.currency = self._get_or_create_gbp_currency()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, firstname, lastname, password):
        """Create and return a superuser."""
        user = self.create_user(email, firstname, lastname, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def _get_or_create_gbp_currency(self):
        """Fetch or create the GBP currency using the API."""
        try:
            # Try to fetch the GBP currency from the database
            return Currency.objects.get(currency="GBP")
        except Currency.DoesNotExist:
            # If GBP doesn't exist, fetch data from the API
            self._fetch_currencies_from_api()
            # Try to fetch GBP again
            return Currency.objects.get(currency="GBP")

    def _fetch_currencies_from_api(self):
        """Fetch currency data from the API and update the database."""
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
            # Handle API failure
            raise ValueError("Failed to fetch exchange rates.")


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model that replaces Django's default auth.User"""
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=128)
    lastname = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    currency = models.ForeignKey(
        'Currency', on_delete=models.SET_NULL, null=True, blank=True)  # Allow blank for initial creation
    notification = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    class Meta:
        verbose_name_plural = "user"

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

    def save(self, *args, **kwargs):
        # Ensure the user has a default currency (GBP)
        if not self.currency:
            self.currency, _ = Currency.objects.get_or_create(
                currency="GBP",
                defaults={"rate": 1.0, "timestamp": 1698765432}  # Default values for GBP
            )
        super().save(*args, **kwargs)


class Currency(models.Model):
    currency = models.CharField(
        primary_key=True, max_length=3)  # e.g., USD, EUR
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    timestamp = models.IntegerField(null=True, blank=True)  # Store the timestamp as an integer

    class Meta:
        verbose_name_plural = "currency"

    def __str__(self):
        return self.currency