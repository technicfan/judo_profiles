from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required, user_passes_test
from django.contrib.auth.models import Group, Permission, User
from django.contrib.sessions.models import Session
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from guardian.shortcuts import assign_perm, remove_perm

from profiles.models import Profile
from profiles.views import unique_username

from .models import Token


# check if user is admin
def is_admin(user):
    return user.is_superuser


# delete all sessions for user
def logout_all(user):
    for s in Session.objects.all():
        if s.get_decoded().get("_auth_user_id") == str(user.id):
            s.delete()


# add user to trainers group
def make_trainer(user):
    group, created = Group.objects.get_or_create(name="Trainers")
    if created:
        permission = Permission.objects.get(codename="add_profile")
        group.permissions.add(permission)
    user.groups.add(group)


@login_not_required
def register(request):
    # not relevant for authenticated users
    if request.user.is_authenticated:
        return redirect("profiles-profiles")
    else:
        if request.method == "POST":
            # register process
            if "username" in request.POST:
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
            # first step (token input)
            elif "token" in request.POST:
                try:
                    token = Token.objects.get(token=request.POST["token"])
                    if token.valid_for < 1:
                        raise Token.DoesNotExist
                except Token.DoesNotExist:
                    # reload with warning if the token is wrong or expired
                    return render(request, "register.html", {"wrong": True})
                username = token.user.username

                # return html for second step (see above)
                return render(
                    request, "register.html", {"username": username, "token": token}
                )
        else:
            # return first step
            return render(request, "register.html", {})


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
                user.token.delete()
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
def logout_user(request):
    logout(request)

    return redirect("profiles-home")


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


@user_passes_test(is_admin)
def users(request):
    if request.method == "POST":
        # get all available users according to request
        users = User.objects.exclude(is_superuser=True).order_by("last_name")
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
                users = users.exclude(groups__name="Trainers")
            case "t":
                users = users.filter(groups__name="Trainers")

        # return html table for htmx
        return render(request, "htmx/users.html", {"users": users})
    else:
        # return template
        return render(request, "users.html")


@user_passes_test(is_admin)
def new_user(request):
    if request.method == "POST":
        # create new trainer with unique username and new token
        newusername = unique_username(
            f"{request.POST['first_name']}.{request.POST['last_name']}"
        )
        newuser = User(
            username=newusername,
            first_name=request.POST["first_name"],
            last_name=request.POST["last_name"],
            is_active=False,
        )
        newuser.save()
        make_trainer(newuser)
        Token(user=newuser).save()

        # redirect to user managing page (see below)
        return redirect("users-user", username=newusername)

    # return template
    return render(request, "users/new.html", {})


@user_passes_test(is_admin)
def manage_user(request, username):
    # load available profile if user exists
    try:
        user = User.objects.get(username=username)
        if user.is_superuser:
            raise User.DoesNotExist
    except User.DoesNotExist:
        return redirect("users-manage")
    profiles = Profile.objects.exclude(user=user).order_by("last_name")

    if request.method == "POST":
        # manage token for user
        if "add" in request.POST:
            Token(user=user).save()
        elif "renew" in request.POST:
            user = user
            user.token.delete()
            Token(user=user).save()
        elif "delete_token" in request.POST:
            user.token.delete()
        elif "reset" in request.POST:
            Token(user=user).save()
            # logout everywhere after creation of token to reset password
            logout_all(user)
        # delete user
        elif "delete" in request.POST:
            user.delete()
        # deactivate user
        elif "deactivate" in request.POST:
            try:
                user.set_unusable_password()
                user.is_active = False
                user.save()
                Token.objects.get(user=user).delete()
            except Token.DoesNotExist:
                pass
            logout_all(user)
        # add user to trainers group
        elif "trainer" in request.POST:
            make_trainer(user)
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

                return HttpResponse("Gespeichert")
            else:
                # return error for htmx
                return HttpResponse("Nicht erlaubt")
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
        # return template
        return render(request, "users/manage.html", {"user": user})
