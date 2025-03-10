from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
<<<<<<< HEAD
from allauth.socialaccount.providers.google.views import OAuth2LoginView
=======
# from allauth.socialaccount.providers.google.views import OAuth2LoginView
>>>>>>> 10032025
from django.urls import reverse
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import login
from django.http import HttpResponse

<<<<<<< HEAD
=======


>>>>>>> 10032025
User = get_user_model()


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            return redirect('login')  # redirect to login page
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('finance:home')
    else:
        form = AuthenticationForm()
        
    return render(request, 'users/login.html', {
        'form': form,
        })


def logout_view(request):
    logout(request)
    
    # Check if the user is authenticated through Google (i.e., if they have a SocialAccount)
    if request.user.is_authenticated and hasattr(request.user, 'socialaccount'):
        return redirect('https://accounts.google.com/Logout')  # Redirect to Google logout if they logged in via Google

    # If the user didn't log in through Google, just redirect them to the login page
    return redirect('login')


def google_login_callback(request):
    if request.user.is_authenticated:
        return redirect('finance:home')  # Redirect to the home page

    try:
        social_account = SocialAccount.objects.get(user=request.user)
        user = social_account.user
        login(request, user)  # Ensure user is logged in
        return redirect('finance:home')
    except SocialAccount.DoesNotExist:
        return redirect('login')

