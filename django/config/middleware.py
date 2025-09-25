import re
from django.shortcuts import redirect
from django.conf import settings


class LoginRequiredMiddleware:
    """Middleware that requires a user to be authenticated to access any page.

    Exemptions can be configured via settings.LOGIN_EXEMPT_URLS (list of regex strings).
    The login URL is taken from settings.LOGIN_URL.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        patterns = getattr(settings, 'LOGIN_EXEMPT_URLS', [])
        # compile regex patterns once
        self.exempt = [re.compile(p) for p in patterns]

    def __call__(self, request):
        # Allow if path matches any exempt pattern
        path = request.path_info
        for p in self.exempt:
            if p.match(path):
                return self.get_response(request)

        # Allow authenticated users
        if getattr(request, 'user', None) and request.user.is_authenticated:
            return self.get_response(request)

        # Not authenticated => redirect to LOGIN_URL
        login_url = getattr(settings, 'LOGIN_URL', '/auth/login')
        # preserve next
        return redirect(f"{login_url}?next={path}")
