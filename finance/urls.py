from django.urls import path, include
from .views import profile_view, settings_view

urlpatterns = [
    path("profile/", profile_view, name ="profile"),
    path("settings/",settings_view, name ="settings"),
]
