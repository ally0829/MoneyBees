from django.urls import path, include
from .views import profile_view
from .views import upcomingExpense_view

urlpatterns = [
    path("profile/", profile_view, name ="profile"),
    path("upcomingExpense/", upcomingExpense_view, name ="upcomingExpense")
]
