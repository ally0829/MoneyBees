from django.urls import path, include
from .views import edit_expense,toggle_notifications,update_expense_target, mark_payment_paid, delete_expense, profile_view, add_income, add_expense, settings_view, expense_record_view, upcomingExpense_view, add_upcoming_payment, edit_upcoming_payment, delete_upcoming_payment, faq_view, home_view, test_email,spending_summary, upcoming_expenses, expense_targets,home_view,categories,get_current_user

app_name = "finance"
urlpatterns = [
    path("profile/", profile_view, name="profile"),
    path("add_income/", add_income, name="add_income"),
    path("add_expense/", add_expense, name="add_expense"),
    path("settings/", settings_view, name="settings"),
    path('faq/', faq_view, name='faq'),
    path('expense-record/', expense_record_view, name='expense_record'),
    path('edit-expense/<int:expense_id>/', edit_expense, name='edit_expense'),
    path('delete-expense/<int:expense_id>/',
         delete_expense, name='delete_expense'),
    path("upcomingExpense/", upcomingExpense_view, name="upcoming_expense"),
    path("add-payment/", add_upcoming_payment, name="add_payment"),
    path("edit-payment/<int:payment_id>/",
         edit_upcoming_payment, name="edit_payment"),
    path("delete-payment/<int:payment_id>/",
         delete_upcoming_payment, name="delete_payment"),
    path('home/', home_view, name='home'),
    path('test-email/', test_email, name='test_email'),
    path('mark-payment-paid/<int:payment_id>/',
         mark_payment_paid, name='mark_payment_paid'),

    path('spending-summary/', spending_summary, name='spending-summary'),
    path('upcoming-expenses/', upcoming_expenses, name='upcoming-expenses'),
    path('expense-targets/', expense_targets, name='expense-targets'),
    path("categories/", categories, name="categories"),
    path("get-current-user/", get_current_user, name="get-current-user"),
    path("expense-targets/<int:target_id>/", update_expense_target, name="update-expense-target"),
    path("toggle-notifications/", toggle_notifications, name="toggle_notifications"),
]
