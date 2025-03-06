from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda request: redirect("login"), name="home"),
    path("users/", include("users.urls")),
    path("finance/", include("finance.urls")),
    path("api/",include("finance.urls"))
]
