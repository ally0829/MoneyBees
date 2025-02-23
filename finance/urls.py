from django.urls import path, include
from .views import profile_view, add_income, add_expense

app_name = "finance"
urlpatterns = [
    path("profile/", profile_view, name ="profile"),
    path("add_income/", add_income, name="add_income"),
    path("add_expense/", add_expense, name="add_expense"),
]
