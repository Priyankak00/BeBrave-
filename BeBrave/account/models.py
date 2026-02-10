import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class AnonymousUserAccount(AbstractUser):
    codename = models.CharField(max_length=100, unique=True)
    is_fully_anonymous = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.codename:
            self.codename = f"Anonymous_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


recovery_hash = models.CharField(max_length=64, blank=True, null=True)
