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

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ..models import Profile, Token
from ..utils import logout_all


def register_start(request):
    try:
        token = Token.objects.get(user__username=request.POST["user"])
        if not token.validate(request.POST["token"]):
            raise Token.DoesNotExist
    except Token.DoesNotExist:
        # reload with warning if the token is wrong or expired
        return render(request, "register.html", {"wrong": True})

    # return html for second step (see above)
    return render(
        request,
        "register.html",
        {"username": request.POST["user"], "token": request.POST["token"]},
    )


def register_finish(request):
    try:
        user = User.objects.get(username=request.POST["username"])
        # check if given passwords are equal
        if request.POST["password"] == request.POST["password_repeat"]:
            token = Token.objects.get(user=user)
            # check if token is correct and still valid
            if not token.validate(request.POST["token"]):
                raise Token.DoesNotExist
            user.set_password(request.POST["password"])
            user.is_active = True
            user.save()
            login(
                request,
                authenticate(
                    request,
                    username=user.username,
                    password=request.POST["password"],
                ),
            )
            # delete now used token
            token.delete()

            # redirect to start
            return redirect("profiles")
        else:
            raise User.DoesNotExist
    except (User.DoesNotExist, Token.DoesNotExist):
        # reload if post data not correct
        return redirect("register")


@require_http_methods(["GET", "POST"])
@login_not_required
def register(request):
    # not relevant for authenticated users
    if request.user.is_authenticated:
        return redirect("profiles")
    else:
        if request.method == "POST":
            # register process
            if "username" in request.POST:
                return register_finish(request)
            # first step (token input)
            elif "token" in request.POST:
                return register_start(request)

            return redirect("register")
        else:
            # return first step
            return render(request, "register.html", {})


@require_http_methods(["GET", "POST"])
@login_not_required
def login_user(request):
    # get path to redirect after login
    next = request.GET.get("next")
    if request.method == "POST":
        user = authenticate(
            request, username=request.POST["user"], password=request.POST["pass"]
        )
        # check if input was correct
        if user is not None:
            # delete token if it exists
            try:
                Token.objects.get(user=user).delete()
            except Token.DoesNotExist:
                pass
            # login the user
            login(request, user)

            if next:
                # redirect to "next"
                return redirect(next)
            else:
                # redirect to start
                return redirect("profiles")
        else:
            # reload with warning
            return render(request, "login.html", {"next": next, "wrong": True})
    else:
        # return template
        return render(request, "login.html", {"next": next})


# simple logout
@require_http_methods(["GET"])
def logout_user(request):
    logout(request)

    return redirect("index")


@require_http_methods(["GET", "POST"])
def account(request):
    if request.method == "POST":
        # delete the user and all data around it
        if "delete" in request.POST:
            for i in Profile.objects.filter(creator=request.user):
                i.creator = i.manager
                i.save()
            for i in Profile.objects.filter(manager=request.user):
                i.manager = i.creator
                i.save()

            request.user.delete()

            return redirect("index")
        # change the password
        else:
            user = authenticate(
                request, username=request.user.username, password=request.POST["pass"]
            )
            # check if request is valid
            if (
                user is not None
                and request.POST["new_pass"] == request.POST["new_pass_confirm"]
            ):
                # update password and logout everywhere
                request.user.set_password(request.POST["new_pass"])
                request.user.save()
                logout_all(request.user)

                # redirect to start
                return redirect("profiles")
            else:
                # reload with warning
                return render(request, "account.html", {"wrong": True})
    else:
        # return template
        return render(request, "account.html")
