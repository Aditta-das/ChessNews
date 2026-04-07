from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def is_online(user):
    if hasattr(user, 'userprofile') and user.userprofile.last_seen:
        return timezone.now() - user.userprofile.last_seen < timedelta(seconds=30)
    return False