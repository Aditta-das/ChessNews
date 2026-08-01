import random
import string
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import timedelta
from ..models import Streak

def generate_unique_username(email):
    base = email.split("@")[0]
    base = ''.join(c for c in base if c.isalnum()).lower()

    if not base:
        base = "user"

    username = base

    while True:
        try:
            with transaction.atomic():
                if not User.objects.filter(username=username).exists():
                    return username
        except IntegrityError:
            pass

        # generate new one if taken
        suffix = ''.join(random.choices(string.digits, k=3))
        username = f"{base}{suffix}"
        

def update_user_streak(user):
    streak, created = Streak.objects.get_or_create(user=user)

    today = timezone.localdate()

    if streak.last_visit is None:
        streak.streak = 1

    elif streak.last_visit == today:
        return

    elif streak.last_visit == today - timedelta(days=1):
        streak.streak += 1

    else:
        streak.streak = 1

    streak.last_visit = today

    if streak.streak > streak.longest_streak:
        streak.longest_streak = streak.streak

    streak.save()