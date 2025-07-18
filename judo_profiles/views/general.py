# Copyright (C) 2025 technicfan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from django.conf import settings
from django.contrib.auth.decorators import (
    login_not_required,
    user_passes_test,
)
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template
from django.views.decorators.http import require_http_methods

from ..models import (
    Profile,
    Server,
    Technique,
)
from ..utils import is_admin


# landing page for non authorized and authorized users
@require_http_methods(["GET"])
@login_not_required
def index(request):
    if request.user.is_authenticated:
        return redirect("profiles")
    else:
        return redirect("about")


@require_http_methods(["GET"])
@login_not_required
def about(request):
    try:
        template = get_template(f"lang/{request.LANGUAGE_CODE}/about.html")
    except TemplateDoesNotExist:
        template = get_template(f"lang/{settings.LANGUAGE_CODE}/about.html")
    return HttpResponse(template.render({}, request))


@require_http_methods(["GET"])
@login_not_required
def privacy(request):
    try:
        template = get_template(f"lang/{request.LANGUAGE_CODE}/privacy.html")
    except TemplateDoesNotExist:
        template = get_template(f"lang/{settings.LANGUAGE_CODE}/privacy.html")
    return HttpResponse(
        template.render({"contact": Server.objects.get(id=1).privacy_contact}, request)
    )


@require_http_methods(["GET"])
@login_not_required
def imprint(request):
    return render(
        request, "imprint.html", {"imprint": Server.objects.get(id=1).imprint}
    )


@require_http_methods(["GET"])
@login_not_required
def license(request):
    return render(request, "license.html", {})


@require_http_methods(["GET", "POST"])
@user_passes_test(is_admin)
def setup(request):
    info = Server.objects.get(id=1)

    if request.method == "POST":
        if request.POST["imprint"] != info.imprint:
            info.imprint = request.POST["imprint"]
        if request.POST["contact"] != info.privacy_contact:
            info.privacy_contact = request.POST["contact"]
        if not info.changed:
            info.changed = True
            info.save()
            return redirect("index")
        info.save()
        return redirect("setup")
    else:
        return render(request, "setup.html", {"info": info})


@require_http_methods(["GET"])
@user_passes_test(is_admin)
def statistics(request):
    techniques = Technique.objects.all()
    context = {
        "profiles": Profile.objects.all().count(),
        "techniques": techniques.count(),
        "standing": techniques.filter(type="S").count(),
        "ground": techniques.filter(type="B").count(),
        "users": User.objects.filter(is_active=True).count(),
        "trainers": User.objects.filter(groups__name="Trainers").count(),
        "staff": User.objects.filter(is_staff=True).count(),
    }
    return render(request, "statistics.html", context)


@require_http_methods(["GET", "POST"])
@user_passes_test(is_admin)
def techniques(request):
    if request.method == "POST":
        if "search" in request.POST:
            # get profiles with search
            techniques = Technique.objects.all()
            search = request.POST["search"]
            filtered = techniques.filter(
                Q(name__icontains=search) | Q(codename__icontains=search)
            ).order_by("codename")

            # return html table for htmx
            return render(request, "htmx/techniques.html", {"techniques": filtered})
        elif "change" in request.POST:
            technique = Technique.objects.get(id=int(request.POST["id"]))
            if not (
                technique.codename == request.POST["codename"]
                and technique.name == request.POST["name"]
                and technique.type == request.POST["type"]
            ):
                technique.codename = request.POST["codename"]
                technique.name = request.POST["name"]
                technique.type = request.POST["type"]
                technique.save()

            return render(
                request,
                "htmx/techniques.html",
                {
                    "techniques": [technique],
                    "changed": True,
                },
            )
        elif "add" in request.POST:
            if (
                request.POST["codename"]
                and request.POST["name"]
                and request.POST["type"]
            ):
                Technique.objects.get_or_create(
                    codename=request.POST["codename"],
                    name=request.POST["name"],
                    type=request.POST["type"],
                )
        elif "delete" in request.POST:
            Technique.objects.get(id=int(request.POST["id"])).delete()
        return HttpResponse()
    else:
        # return template
        return render(request, "techniques.html")
