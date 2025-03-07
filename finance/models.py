from django.db import models
from django.contrib.auth.models import AbstractUser
from users.models import User
from users.models import Currency

class ExpenseCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = "expense_category"

    def __str__(self):
        return self.name


class IncomeCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = "income_category"

    def __str__(self):
        return self.name


class Income(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateField()
    description = models.CharField(max_length=256, default="")
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)  
    category = models.ForeignKey(
        IncomeCategory, on_delete=models.CASCADE, default=1)

    class Meta:
        verbose_name_plural = "income"

    def __str__(self):
        return f"{self.user.firstname} - {self.amount}"


class Expense(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateField()
    description = models.CharField(max_length=255, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)  

    class Meta:
        verbose_name_plural = "expense"

    def __str__(self):
        return f"{self.user.firstname} - {self.amount} in {self.category.name}"


class MonthlyExpenseTarget(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    month = models.IntegerField()

    class Meta:
        verbose_name_plural = "monthly_expense_target"

    def __str__(self):
        return f"{self.user.firstname} - {self.amount} for {self.category.name}"


class UpcomingPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.firstname} - {self.category.name} - {self.amount} on {self.date}"
    

# users/models.py

class ExchangeRate(models.Model):
    success = models.BooleanField() #true false
    timestamp = models.BigIntegerField() # 1741259771
    base = models.CharField(max_length=3) # EUR
    date = models.DateField() #"2025-03-06"
    rates = models.JSONField()  # {AED: 3.231323 , AFN, 77.2323 etc...}

    def __str__(self):
        return f"Exchange rates for {self.base} on {self.date}"