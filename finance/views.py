from django.shortcuts import render
from .models import ExpenseCategory

# Create your views here.
def profile_view(request):
    return render(request, 'finance/profile.html',{"show_topbar": False}),


def upcomingExpense_view(request):
    categories=ExpenseCategory.objects.all()
    return render(request, 'finance/upcomingExpense.html',{"show_topbar": True,'categories': categories})


