from django.shortcuts import redirect
from django.urls import reverse

from ..models import Server


class SetupRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.path != reverse("setup")
            and request.path != reverse("logout")
            and request.user.is_superuser
            and not Server.objects.get(id=1).changed
        ):
            return redirect("setup")

        return self.get_response(request)
