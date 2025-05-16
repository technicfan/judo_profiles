from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from django.views.decorators.http import require_http_methods
from guardian.shortcuts import assign_perm, remove_perm

from ..models import Profile, Token
from ..utils import (
    is_admin,
    is_staff,
    logout_all,
    toggle_trainer,
    token_actions,
    unique_username,
    user_actions,
)


def register_start(request):
    try:
        token = Token.objects.get(
            token=request.POST["token"], user__username=request.POST["user"]
        )
        if token.valid_for < 1:
            raise Token.DoesNotExist
    except Token.DoesNotExist:
        # reload with warning if the token is wrong or expired
        return render(request, "register.html", {"wrong": True})

    # return html for second step (see above)
    return render(
        request, "register.html", {"username": request.POST["user"], "token": token}
    )


def register_finish(request):
    try:
        user = User.objects.get(username=request.POST["username"])
        # check if given passwords are equal
        if request.POST["password"] == request.POST["password_repeat"]:
            token = Token.objects.get(user=user)
            # check if token is correct and still valid
            if request.POST["token"] != token.token or token.valid_for < 1:
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
            return redirect("profiles-profiles")
        else:
            raise User.DoesNotExist
    except (User.DoesNotExist, Token.DoesNotExist):
        # reload if post data not correct
        return redirect("users-register")


@require_http_methods(["GET", "POST"])
@login_not_required
def register(request):
    # not relevant for authenticated users
    if request.user.is_authenticated:
        return redirect("profiles-profiles")
    else:
        if request.method == "POST":
            # register process
            if "username" in request.POST:
                return register_finish(request)
            # first step (token input)
            elif "token" in request.POST:
                return register_start(request)

            return redirect("users-register")
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
                return redirect("profiles-profiles")
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

    return redirect("profiles-home")


@require_http_methods(["GET", "POST"])
def change_pass(request):
    if request.method == "POST":
        # delete the user and all data around it
        if "delete" in request.POST:
            request.user.delete()

            return redirect("profiles-home")
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
                return redirect("profiles-profiles")
            else:
                # reload with warning
                return render(request, "account.html", {"wrong": True})
    else:
        # return template
        return render(request, "account.html")


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
        Token(user=newuser).save()

        # redirect to user managing page (see below)
        return redirect("users-user", username=newusername)

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
        return redirect("users-manage")
    profiles = Profile.objects.exclude(user=user).order_by("last_name")

    if request.method == "POST":
        # manage token for user
        if "token" in request.POST:
            token_actions(request.POST, user, True)
        # manage user
        elif "user" in request.POST:
            user_actions(request.POST, user, request.user.is_superuser)
        # change permissions
        elif "update" in request.POST:
            permission = request.POST["permission"]
            permissions = ["view_profile"]
            # more permissions if trainer
            if user.groups.filter(name="Trainers").exists():
                permissions += ["change_profile", "manage_profile"]
            # check if permission is allowed
            if permission in permissions:
                # see "manage_profile" for functionality
                remove = profiles
                for id in request.POST:
                    if id.isdigit():
                        try:
                            profile = Profile.objects.get(id=int(id))
                            for p in permissions[: permissions.index(permission) + 1]:
                                assign_perm(p, user, profile)
                            remove = remove.exclude(id=int(id))
                        except (Profile.DoesNotExist, ValueError):
                            pass

                for profile in remove:
                    for p in permissions[permissions.index(permission) :]:
                        remove_perm(p, user, profile)

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
        return redirect("users-user", username=username)
    else:
        # get plural translation
        try:
            count = Token.objects.get(user=user).valid_for
            days = ngettext(
                "Valid for %(count)d day", "Valid for %(count)d days", count
            ) % {"count": count}
        except Token.DoesNotExist:
            days = None

        # return template
        return render(request, "users/manage.html", {"user": user, "days": days})
