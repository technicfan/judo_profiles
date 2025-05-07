import re

from django.conf import settings
from django.contrib.auth.middleware import LoginRequiredMiddleware

# credits to https://code.djangoproject.com/ticket/35932


class CustomLoginRequiredMiddleware(LoginRequiredMiddleware):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.exempt_urls = [
            re.compile(pattern) for pattern in settings.LOGIN_REQUIRED_EXCEPTIONS
        ]

    def process_view(self, request, view_func, *args, **kwargs):
        if request.user.is_authenticated:
            return None

        if not getattr(view_func, "login_required", True):
            return None

        if any(pattern.match(request.path_info) for pattern in self.exempt_urls):
            return None

        return self.handle_no_permission(request, view_func)
