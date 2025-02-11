from django.urls import path
from . import views  # Assuming you have a `views.py` in your users app

urlpatterns = [
    path('', views.login_view, name='login'), #default to login view
]
