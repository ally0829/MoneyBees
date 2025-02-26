from django.urls import path
from .views import (
    upcomingExpense_view, 
    add_upcoming_payment, 
    edit_upcoming_payment, 
    delete_upcoming_payment
)

urlpatterns = [
    path("upcomingExpense/", upcomingExpense_view, name="upcoming_expense"),
    path("add-payment/", add_upcoming_payment, name="add_payment"),
    path("edit-payment/<int:payment_id>/", edit_upcoming_payment, name="edit_payment"),
    path("delete-payment/<int:payment_id>/", delete_upcoming_payment, name="delete_payment"),
]
