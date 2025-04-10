from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group, Permission
from django.contrib.sessions.models import Session
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required, user_passes_test
from guardian.shortcuts import assign_perm, remove_perm

from profiles.views import unique_username
from profiles.models import Profile
from .models import Token


def is_admin(user):
    return user.is_superuser


def logout_all(user):
    for s in Session.objects.all():
        if s.get_decoded().get('_auth_user_id') == str(user.id):
            s.delete()


def make_trainer(user):
    group, created = Group.objects.get_or_create(name="Trainers")
    permission = Permission.objects.get(codename="add_profile")
    if created:
        group.permissions.add(permission)
    user.groups.add(group)


@login_not_required
def register(request):
    if request.user.is_authenticated:
        return redirect("profiles-profiles")
    else:
        if request.method == "POST":
            if "token" in request.POST:
                try:
                    token = Token.objects.get(token=request.POST["token"])
                    if token.valid_for < 1:
                        raise Token.DoesNotExist
                except Token.DoesNotExist:
                    return render(request, "register.html", {"wrong": True})
                username = token.user.username

                return render(request, "register.html", {"username": username, "post": True})
            elif "username" in request.POST:
                try:
                    user = User.objects.get(username=request.POST["username"])
                    if request.POST["password"] == request.POST["password_repeat"]:
                        token = Token.objects.get(user=user)
                        if token.valid_for < 1:
                            raise Token.DoesNotExist
                        user.set_password(request.POST["password"])
                        user.is_active = True
                        user.save()
                        login(
                            request,
                            authenticate(
                                request,
                                username=user.username,
                                password=request.POST["password"]
                            )
                        )
                        token.delete()

                        return redirect("profiles-profiles")
                    else:
                        raise User.DoesNotExist
                except (User.DoesNotExist, Token.DoesNotExist):
                    return redirect("users-register")
            else:
                return redirect("users-register")
        else:
            return render(request, "register.html", {})


@login_not_required
def login_user(request):
    next = request.GET.get("next")
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["user"],
            password=request.POST["pass"]
        )
        if user is not None:
            try:
                user.token.delete()
            except Token.DoesNotExist:
                pass
            login(request, user)

            if next:
                return redirect(next)
            else:
                return redirect("profiles-profiles")
        else:
            return render(request, "login.html", {"next": next, "wrong": True})
    else:
        return render(request, "login.html", {"next": next})


def logout_user(request):
    logout(request)

    return redirect("profiles-home")


def change_pass(request):
    if request.method == "POST":
        if "delete" in request.POST:
            request.user.delete()

            return redirect("profiles-home")
        else:
            user = authenticate(
                request,
                username=request.user.username,
                password=request.POST["pass"]
            )
            if user is not None and request.POST["new_pass"] == request.POST["new_pass_confirm"]:
                request.user.set_password(request.POST["new_pass"])
                request.user.save()
                logout_all(request.user)

                return redirect("profiles-profiles")
            else:
                return render(request, "account.html", {"wrong": True})
    else:
        return render(request, "account.html")


@user_passes_test(is_admin)
def manage_users(request):
    if request.method == "POST":
        users = User.objects.exclude(is_superuser=True).order_by("last_name")
        users = users.filter(
            Q(first_name__icontains=request.POST["search"]) |
            Q(last_name__icontains=request.POST["search"])).order_by("last_name"
        )

        match(request.POST["status"]):
            case "a":
                users = users.exclude(is_active=False)
            case "i":
                users = users.filter(is_active=False)

        match(request.POST["type"]):
            case "u":
                users = users.exclude(groups__name="Trainers")
            case "t":
                users = users.filter(groups__name="Trainers")

        return render(request, "htmx/users.html", {"users": users})
    else:
        return render(request, "users.html")


@user_passes_test(is_admin)
def new_user(request):
    if request.method == "POST":
        newusername = unique_username(f"{request.POST["first_name"]}.{request.POST["last_name"]}")
        newuser = User(
            username=newusername,
            first_name=request.POST["first_name"],
            last_name=request.POST["last_name"],
            is_active=False
        )
        newuser.save()
        make_trainer(newuser)
        Token(user=newuser).save()

        return redirect("users-user", username=newusername)

    return render(request, "users/new.html", {})


@user_passes_test(is_admin)
def user_permissions(request, username):
    try:
        user = User.objects.get(username=username)
        if user.is_superuser:
            raise User.DoesNotExist
    except User.DoesNotExist:
        return redirect("users-manage")
    profiles = Profile.objects.exclude(user=user).order_by("last_name")

    if request.method == "POST":
        if "add" in request.POST:
            Token(user=user).save()
        elif "renew" in request.POST:
            user = user
            user.token.delete()
            Token(user=user).save()
        elif "delete_token" in request.POST:
            user.token.delete()
        elif "reset" in request.POST:
            logout_all(user)
            Token(user=user).save()
        elif "delete" in request.POST:
            user.delete()
        elif "deactivate" in request.POST:
            try:
                user.set_unusable_password()
                user.is_active = False
                user.save()
                Token.objects.get(user=user).delete()
            except Token.DoesNotExist:
                pass
            logout_all(user)
        elif "trainer" in request.POST:
            make_trainer(user)
        elif "update" in request.POST:
            permission = request.POST["permission"]
            permissions = [
                "view_profile",
                "change_profile",
                "manage_profile"
            ]
            remove = profiles
            for id in request.POST:
                if id.isdigit():
                    try:
                        profile = Profile.objects.get(id=int(id))
                        for p in permissions[:permissions.index(permission) + 1]:
                            assign_perm(p, user, profile)
                        remove = remove.exclude(id=int(id))
                    except (Profile.DoesNotExist, ValueError):
                        pass

            for profile in remove:
                for p in permissions[permissions.index(permission):]:
                    remove_perm(p, user, profile)

            return HttpResponse("Gespeichert")
        elif "search" in request.POST:
            search = request.POST["search"]
            permission = request.POST["permission"]
            filtered = profiles.filter(Q(name__icontains=search) | Q(last_name__icontains=search))
            if filtered.count() == 0:
                filtered = None

            return render(request, "htmx/user_permissions.html", {
                "profiles": filtered,
                "user": user,
                "permission": permission
            })

        return redirect("users-user", username=username)
    else:

        return render(request, "users/manage.html", {"user": user})
