from django.shortcuts import redirect
from functools import wraps

def premium_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, 'userprofile', None)
        if profile and profile.has_active_premium():
            return view_func(request, *args, **kwargs)
        return redirect('buy_premium')
    return wrapper
