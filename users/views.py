from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login

def login_view(request):
    # renders the base html for now, should change it to login.html when created, base html is for extensions only!
    return render(request, 'finance/profile.html') 
