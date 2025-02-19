from django.urls import path, include
from .views import profile_view

urlpatterns = [
    path("profile/", profile_view, name ="profile"),
]
