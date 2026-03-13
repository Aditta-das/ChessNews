import random
import string
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction

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