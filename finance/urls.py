from django.urls import path, include
from .views import profile_view, add_income, add_expense, settings_view, expense_record_view, upcomingExpense_view, add_upcoming_payment, edit_upcoming_payment, delete_upcoming_payment, faq_view, home_view

app_name = "finance"
urlpatterns = [
    path("profile/", profile_view, name="profile"),
    path("add_income/", add_income, name="add_income"),
    path("add_expense/", add_expense, name="add_expense"),
    path("settings/", settings_view, name="settings"),
    path('faq/', faq_view, name='faq'),
    path('expense-record/', expense_record_view, name='expense_record'),
    path("upcomingExpense/", upcomingExpense_view, name="upcoming_expense"),
    path("add-payment/", add_upcoming_payment, name="add_payment"),
    path("edit-payment/<int:payment_id>/",
         edit_upcoming_payment, name="edit_payment"),
    path("delete-payment/<int:payment_id>/",
         delete_upcoming_payment, name="delete_payment"),
    path('home/', home_view, name='home'),  # mock homepage
]
