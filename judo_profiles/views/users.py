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

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from django.views.decorators.http import require_http_methods
from guardian.shortcuts import assign_perm, remove_perm

from ..models import Profile, Server
from ..utils import (
    is_admin,
    is_staff,
    toggle_trainer,
    token_actions,
    unique_username,
    user_actions,
)


@require_http_methods(["GET", "POST"])
@user_passes_test(is_staff)
def users(request):
    if request.method == "POST":
        # get all available users according to request
        users = (
            User.objects.exclude(is_superuser=True)
            .exclude(id=request.user.id)
            .order_by("last_name")
        )
        users = users.filter(
            Q(first_name__icontains=request.POST["search"])
            | Q(last_name__icontains=request.POST["search"])
        ).order_by("last_name")

        # filter by status
        match request.POST["status"]:
            case "a":
                users = users.exclude(is_active=False)
            case "i":
                users = users.filter(is_active=False)

        # filter by type
        match request.POST["type"]:
            case "u":
                users = users.exclude(groups__name="Trainers").exclude(is_staff=True)
            case "t":
                users = users.filter(groups__name="Trainers")
            case "s":
                users = users.filter(is_staff=True)

        # return html table for htmx
        return render(request, "htmx/users.html", {"users": users})
    else:
        # return template
        return render(request, "users.html")


def new_user(request, staff: bool):
    if request.method == "POST":
        # create new user with unique username and new token
        newusername = unique_username(
            f"{request.POST['first_name']}.{request.POST['last_name']}"
        )
        newuser = User(
            username=newusername,
            first_name=request.POST["first_name"],
            last_name=request.POST["last_name"],
            is_active=False,
        )
        if staff:
            newuser.is_staff = True
            newuser.save()
        else:
            newuser.save()
            toggle_trainer(newuser)

        # redirect to user managing page (see below)
        return redirect("manage-user", username=newusername)

    # return template
    return render(request, "users/new.html", {"staff": staff})


@require_http_methods(["GET", "POST"])
@user_passes_test(is_staff)
def new_trainer(request):
    return new_user(request, False)


@require_http_methods(["GET", "POST"])
@user_passes_test(is_admin)
def new_staff(request):
    return new_user(request, True)


@require_http_methods(["GET", "POST"])
@user_passes_test(is_staff)
def manage_user(request, username):
    # load available profiles if user exists
    try:
        user = User.objects.get(username=username)
        if (
            user.is_superuser
            or user == request.user
            or (user.is_staff and not request.user.is_superuser)
        ):
            raise User.DoesNotExist
    except User.DoesNotExist:
        return redirect("users")
    profiles = Profile.objects.exclude(user=user).order_by("last_name")

    if request.method == "POST":
        # manage token for user
        if "token" in request.POST:
            result = token_actions(request.POST, user, True)
            if result is not None:
                return render(request, "htmx/token.html", {"token": result})
        # manage user
        elif "user" in request.POST:
            user_actions(request.POST, user, request.user.is_superuser)
        # change permissions
        elif "update" in request.POST:
            permission = request.POST["permission"]
            permissions = ["view_profile"]
            # more permissions if trainer
            if user.groups.filter(name="Trainers").exists():
                permissions += ["change_profile"]
            # check if permission is allowed
            if permission in permissions:
                # see "manage_profile" for explanation
                remove = profiles
                for id in request.POST:
                    if id.isdigit():
                        try:
                            profile = Profile.objects.get(id=int(id))
                            assign_perm(permission, user, profile)
                            if permission != "view_profile":
                                assign_perm("view_profile", user, profile)
                            remove = remove.exclude(id=int(id))
                        except (Profile.DoesNotExist, ValueError):
                            pass

                for profile in remove:
                    if permission == "view_profile":
                        for p in permissions:
                            remove_perm(p, user, profile)
                    else:
                        remove_perm(permission, user, profile)

                return HttpResponse(_("Saved"))
            else:
                # return error for htmx
                return HttpResponse(_("Not allowed"))
        elif "search" in request.POST:
            # filter profiles according to request
            search = request.POST["search"]
            permission = request.POST["permission"]
            filtered = profiles.filter(
                Q(name__icontains=search) | Q(last_name__icontains=search)
            )
            if filtered.count() == 0:
                filtered = None

            # return html table for htmx
            return render(
                request,
                "htmx/user_permissions.html",
                {"profiles": filtered, "user": user, "permission": permission},
            )

        # reload page
        return redirect("manage-user", username=username)
    else:
        # get plural translation
        days = ngettext(
            "Valid for %(count)d day",
            "Valid for %(count)d days",
            Server.objects.get(id=1).token_expiration,
        ) % {"count": Server.objects.get(id=1).token_expiration}

        # return template
        return render(request, "users/manage.html", {"user": user, "days": days})
