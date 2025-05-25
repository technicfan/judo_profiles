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
def contact(request):
    return render(
        request, "contact.html", {"contact": Server.objects.get(id=1).legal_info}
    )


@require_http_methods(["GET", "POST"])
@user_passes_test(is_admin)
def setup(request):
    info, _ = Server.objects.get_or_create(id=1)

    if request.method == "POST":
        if request.POST["info"] != info.legal_info:
            info.legal_info = request.POST["info"]
            print("1")
        if request.POST["contact"] != info.privacy_contact:
            info.privacy_contact = request.POST["contact"]
        if not info.changed:
            info.changed = True
        info.save()
        print(request.POST)
        print(info.legal_info)

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
