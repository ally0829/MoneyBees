from django.test import TestCase, Client

# Create your tests here.
from finance.models import (
    ExpenseCategory, IncomeCategory, Income, Expense, 
    MonthlyExpenseTarget, UpcomingPayment, Currency
)
from users.models import User, Currency

from datetime import date


from django.urls import reverse
from django.contrib.auth import get_user_model
import json


class FinanceModelsTestCase(TestCase):
    def setUp(self):
        """Set up data for testing."""
        self.currency = Currency.objects.create(currency="USD", rate=1.0, timestamp=1698765432)
        self.user = User.objects.create(email="pragati@gmail.com", firstname="*", lastname="Pragati", currency = self.currency)
        self.expense_category = ExpenseCategory.objects.create(name="Food")
        self.income_category = IncomeCategory.objects.create(name="Salary", description="Monthly salary")
        
        self.income = Income.objects.create(
            user=self.user,
            amount=5000.00,
            date=date.today(),
            description="Monthly Salary",
            currency=self.currency,
            category=self.income_category,
        )

        self.expense = Expense.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=100.00,
            date=date.today(),
            description="Lunch",
            currency=self.currency,
        )

        self.monthly_target = MonthlyExpenseTarget.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=300.00,
            month=3,
        )


    def test_expense_category_str(self):
        self.assertEqual(str(self.expense_category), "Food")

    def test_income_category_str(self):
        self.assertEqual(str(self.income_category), "Salary")

    def test_income_str(self):
        self.assertEqual(str(self.income), f"{self.user.firstname} - {self.income.amount:.1f}")

    def test_expense_str(self):
        self.assertEqual(str(self.expense), f"{self.user.firstname} - {self.expense.amount:.1f} in {self.expense.category}")

    def test_monthly_expense_target_str(self):
        self.assertEqual(str(self.monthly_target), f"{self.user.firstname} - {self.monthly_target.amount:.1f} for {self.monthly_target.category}")

    def test_income_creation(self):
        """Ensure the income object is created correctly."""
        self.assertEqual(Income.objects.count(), 1)
        self.assertEqual(self.income.amount, 5000.00)
        self.assertEqual(self.income.category, self.income_category)

    def test_expense_creation(self):
        """Ensure the expense object is created correctly."""
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(self.expense.amount, 100.00)
        self.assertEqual(self.expense.category, self.expense_category)

    def test_monthly_target_creation(self):
        """Ensure the monthly expense target object is created correctly."""
        self.assertEqual(MonthlyExpenseTarget.objects.count(), 1)
        self.assertEqual(self.monthly_target.amount, 300.00)
        self.assertEqual(self.monthly_target.month, 3)
