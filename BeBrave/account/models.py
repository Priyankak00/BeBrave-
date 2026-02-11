import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

class AnonymousUserAccount(AbstractUser):
    codename = models.CharField(max_length=100, unique=True)
    is_fully_anonymous = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.codename:
            self.codename = f"Anonymous_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class ProfileEntry(models.Model):
    MOOD_CHOICES = [
        ('low', 'Low'),
        ('uneasy', 'Uneasy'),
        ('okay', 'Okay'),
        ('bright', 'Bright'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile_entries'
    )
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    stress_level = models.PositiveSmallIntegerField()
    sleep_hours = models.DecimalField(max_digits=4, decimal_places=1)
    weekly_calm = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class DailyMood(models.Model):
    MOOD_CHOICES = ProfileEntry.MOOD_CHOICES

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_moods'
    )
    date = models.DateField()
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']


class JournalEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='journal_entries'
    )
    title = models.CharField(max_length=120, blank=True)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


recovery_hash = models.CharField(max_length=64, blank=True, null=True)
