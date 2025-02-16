from django.contrib import admin

from .models import User, Currency
# Register your models here.

admin.site.register(User)
admin.site.register(Currency)

