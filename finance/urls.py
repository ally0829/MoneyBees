from django.urls import path, include
from .views import profile_view, add_income, add_expense, settings_view, expense_record_view

app_name = "finance"
urlpatterns = [
    path("profile/", profile_view, name ="profile"),
    path("add_income/", add_income, name="add_income"),
    path("add_expense/", add_expense, name="add_expense"),
    path("settings/",settings_view, name ="settings"),
    path('expense-record/', expense_record_view, name='expense_record'),
]
