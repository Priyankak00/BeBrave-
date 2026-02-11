from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from account.models import DailyMood, JournalEntry, ProfileEntry

# Create your views here.
@login_required
def dashboard_home(request):
    today = date.today()
    if request.method == "POST":
        mood = (request.POST.get('mood') or '').strip()
        if mood:
            DailyMood.objects.update_or_create(
                user=request.user,
                date=today,
                defaults={'mood': mood}
            )
    streak = 0
    day_cursor = today
    while True:
        if DailyMood.objects.filter(user=request.user, date=day_cursor).exists():
            streak += 1
            day_cursor -= timedelta(days=1)
        else:
            break

    week_start = today - timedelta(days=6)
    recent_moods = list(DailyMood.objects.filter(
        user=request.user,
        date__gte=week_start,
        date__lte=today
    ))
    if recent_moods:
        mood_weights = {
            'low': 30,
            'uneasy': 50,
            'okay': 70,
            'bright': 90,
        }
        total_weight = 0
        weighted_sum = 0
        for entry in recent_moods:
            days_ago = (today - entry.date).days
            recency = max(1, 7 - days_ago)
            score = mood_weights.get(entry.mood, 50)
            total_weight += recency
            weighted_sum += score * recency
        mood_balance = int(round(weighted_sum / total_weight)) if total_weight else 0
    else:
        mood_balance = 0

    note_count = JournalEntry.objects.filter(user=request.user).count()
    last_note = JournalEntry.objects.filter(user=request.user).first()

    today_mood = DailyMood.objects.filter(user=request.user, date=today).first()
    mood_key = today_mood.mood if today_mood else None
    suggestions = {
        'low': {
            'title': 'Grounding Breath',
            'desc': 'Try a 2-minute 4-6 breathing rhythm to slow the noise.',
            'cta': 'Start grounding',
            'seconds': 120,
            'done': 'You completed a grounding reset. Well done.'
        },
        'uneasy': {
            'title': 'Reset Walk',
            'desc': 'A short, slow walk with a 3-step inhale, 4-step exhale.',
            'cta': 'Begin reset',
            'seconds': 180,
            'done': 'Nice work. Your reset walk is complete.'
        },
        'okay': {
            'title': 'Focus Sprint',
            'desc': '10-minute focus sprint with a single intention.',
            'cta': 'Start focus',
            'seconds': 600,
            'done': 'Great focus. You finished your sprint.'
        },
        'bright': {
            'title': 'Gratitude Note',
            'desc': 'Write three small wins from today in your journal.',
            'cta': 'Write now',
            'seconds': 120,
            'done': 'Yay! Gratitude logged.'
        },
    }
    suggestion = suggestions.get(mood_key, {
        'title': 'Gentle Check-in',
        'desc': 'Pick a mood to get a tailored suggestion.',
        'cta': 'Select mood',
        'seconds': 0,
        'done': 'Nice work showing up today.'
    })

    context = {
        'calm_streak_days': streak,
        'mood_balance_pct': mood_balance,
        'private_notes_count': note_count,
        'last_note_time': last_note.created_at if last_note else None,
        'today_mood': mood_key,
        'suggestion': suggestion,
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def journal_view(request):
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
    return render(request, 'dashboard/journal.html', context)

