import uuid
from datetime import date
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import AnonymousUserAccount, DailyMood, JournalEntry, ProfileEntry

# Create your views here.

def anonymous_user_view(request):
    return render(request, 'account/anonymous_user.html')

def _predict_weekly_calm(mood, stress_level, sleep_hours):
    mood_base = {
        'low': 35,
        'uneasy': 50,
        'okay': 65,
        'bright': 80,
    }.get(mood, 50)

    sleep_bonus = min(max(sleep_hours, 0), 10) * 2
    stress_penalty = min(max(stress_level, 1), 5) * 6
    score = int(round(mood_base + sleep_bonus - stress_penalty))
    return max(0, min(score, 100))


@login_required
def user_profile_view(request):
    context = {}
    today = date.today()
    today_entry = DailyMood.objects.filter(user=request.user, date=today).first()
    context['today_mood'] = today_entry.mood if today_entry else None
    if request.method == "POST":
        mood = (request.POST.get('mood') or '').strip()
        stress_level_raw = request.POST.get('stress_level')
        sleep_hours_raw = request.POST.get('sleep_hours')

        try:
            stress_level = int(stress_level_raw)
            sleep_hours = float(sleep_hours_raw)
        except (TypeError, ValueError):
            context['error'] = 'Please provide valid stress and sleep values.'
        else:
            DailyMood.objects.update_or_create(
                user=request.user,
                date=today,
                defaults={'mood': mood}
            )
            weekly_calm = _predict_weekly_calm(mood, stress_level, sleep_hours)
            entry = ProfileEntry.objects.create(
                user=request.user,
                mood=mood,
                stress_level=stress_level,
                sleep_hours=sleep_hours,
                weekly_calm=weekly_calm
            )
            context['prediction'] = weekly_calm
            context['entry'] = entry
            context['today_mood'] = mood

    context['recent_entries'] = ProfileEntry.objects.filter(user=request.user)[:5]
    return render(request, 'account/user_profile.html', context)

def quick_signup(request):
    if request.method == "POST":
        username = (request.POST.get('username') or '').strip()
        if username and AnonymousUserAccount.objects.filter(username=username).exists():
            return render(request, 'account/sign_up.html', {
                'error': 'That username is already taken. Please choose another.'
            })
        if not username:
            username = f"user_{uuid.uuid4().hex[:10]}"
        user = AnonymousUserAccount.objects.create_user(
            username=username,
            password=request.POST.get('password'),
            is_fully_anonymous=True
        )
        login(request, user)
        return redirect('dashboard:dashboard_home')
    return render(request, 'account/sign_up.html')  

def login_view(request):
    if request.method == "POST":
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard:dashboard_home')
        return render(request, 'account/login.html', {
            'error': 'Invalid username or password.'
        })
    return render(request, 'account/login.html')

def dashboard_view(request):
    return render(request, 'account/dashboard/home.html')


@login_required
def journal_editor(request):
    context = {}
    if request.method == "POST":
        title = (request.POST.get('title') or '').strip()
        body = (request.POST.get('body') or '').strip()
        if not body:
            context['error'] = 'Please write something before saving.'
        else:
            JournalEntry.objects.create(
                user=request.user,
                title=title,
                body=body
            )
            context['success'] = 'Saved to your private journal.'

    context['recent_entries'] = JournalEntry.objects.filter(user=request.user)[:5]
    return render(request, 'account/journal_editor.html', context)