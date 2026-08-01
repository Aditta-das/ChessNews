from django.utils import timezone
from news.services.utils import update_user_streak


class LastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = request.user.userprofile
            profile.last_seen = timezone.now()
            profile.save(update_fields=['last_seen'])

        return self.get_response(request)

class UserStreakMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            update_user_streak(request.user)

        return self.get_response(request)