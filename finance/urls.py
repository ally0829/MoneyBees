from django.urls import path, include
from .views import profile_view, expense_record_view

urlpatterns = [
    path("profile/", profile_view, name="profile"),
    path('expense-record/', expense_record_view, name='expense_record'),
]
