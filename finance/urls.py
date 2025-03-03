from django.urls import path, include
<<<<<<< HEAD
from .views import profile_view, settings_view

urlpatterns = [
    path("profile/", profile_view, name ="profile"),
    path("settings/",settings_view, name ="settings"),
=======
from .views import profile_view, add_income, add_expense

app_name = "finance"
urlpatterns = [
    path("profile/", profile_view, name ="profile"),
    path("add_income/", add_income, name="add_income"),
    path("add_expense/", add_expense, name="add_expense"),
>>>>>>> 03032025
]
