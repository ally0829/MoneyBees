from django.shortcuts import render
import json
from django.shortcuts import render
from django.conf import settings

# Create your views here.
def profile_view(request):
    return render(request, 'finance/profile.html',{"show_topbar": False})

def settings_view(request):
     # Get the absolute path of the JSON file
    json_path = settings.DATA_DIR / 'currencies.json'

    # Load the JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        currencies = json.load(f)

    return render(request, 'finance/settings.html',{'currencies': currencies})
