import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import AnonymousUserAccount

# Create your views here.

def anonymous_user_view(request):
    return render(request, 'account/anonymous_user.html')

def user_profile_view(request):
    return render(request, 'account/user_profile.html')

def quick_signup(request):
    if request.method == "POST":
        user = AnonymousUserAccount.objects.create_user(
            username=f"user_{uuid.uuid4().hex[:10]}",
            password=request.POST.get('password'),
            is_fully_anonymous=True
        )
        login(request, user)
        return redirect('dashboard:dashboard_home')
    return render(request, 'sign_up.html')

def dashboard_view(request):
    return render(request, 'account/dashboard/home.html')