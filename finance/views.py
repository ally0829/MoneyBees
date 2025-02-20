from django.shortcuts import render

# Create your views here.
def profile_view(request):
    return render(request, 'finance/profile.html',{"show_topbar": False})
