from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required, user_passes_test

from profiles.views import unique_username
from .models import Token


def is_admin(user):
    return user.is_superuser


@login_not_required
def register(request):
    if request.method == "POST":
        if "token" in request.POST:
            try:
                token = Token.objects.get(token=request.POST["token"])
                if token.valid_for < 1:
                    # token.user.delete()
                    raise Token.DoesNotExist
            except Token.DoesNotExist:
                return HttpResponseRedirect("")
            username = token.user.username

            return render(request, "register.html", {"username": username, "post": True})
        elif "username" in request.POST:
            try:
                user = User.objects.get(username=request.POST["username"])
                if request.POST["password"] == request.POST["password_repeat"]:
                    token = Token.objects.get(user=user)
                    if token.valid_for < 1:
                        # token.user.delete()
                        raise Token.DoesNotExist
                    user.set_password(request.POST["password"])
                    user.is_active = True
                    # if token.trainer:
                    #     permission = Permission.objects.get(codename="add_profile")
                    #     group, created = Group.objects.get_or_create(name="Trainers")
                    #     if created:
                    #         group.permissions.add(permission)
                    #     user.groups.add(group)
                    user.save()
                    login(request, authenticate(request, username=user.username, password=request.POST["password"]))
                    token.delete()

                    return HttpResponseRedirect("/")
                else:
                    raise User.DoesNotExist
            except (User.DoesNotExist, Token.DoesNotExist):
                return HttpResponseRedirect("")
        else:
            return HttpResponseRedirect("")
    else:
        return render(request, "register.html", {})


@login_not_required
def login_user(request):
    next = request.GET.get("next")
    if request.method == "POST":
        user = authenticate(request, username=request.POST["user"], password=request.POST["pass"])
        if user is not None:
            login(request, user)

            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect("/")
        else:
            return render(request, "login.html", {"next": next})
    else:
        return render(request, "login.html", {"next": next})


def logout_user(request):
    logout(request)

    return HttpResponseRedirect("/")


def change_pass(request):
    if request.method == "POST":
        user = authenticate(request, username=request.user.username, password=request.POST["pass"])
        if user is not None and request.POST["new_pass"] == request.POST["new_pass_confirm"]:
            request.user.set_password(request.POST["new_pass"])
            request.user.save()
            logout(request)

            return HttpResponseRedirect("/")
        else:
            return render(request, "update.html")
    else:
        return render(request, "update.html")


@user_passes_test(is_admin)
def manage_users(request):
    if request.method == "POST":
        if "delete" in request.POST:
            try:
                User.objects.get(username=request.POST["delete"]).delete()
            except User.DoesNotExist:
                pass
        elif "deactivate" in request.POST:
            try:
                user = User.objects.get(username=request.POST["deactivate"])
                user.set_unusable_password()
                user.is_active = False
                user.save()
                Token.objects.get(user=user).delete()
            except (User.DoesNotExist, Token.DoesNotExist):
                pass
        elif "activate" in request.POST:
            print("cool")
            try:
                user = User.objects.get(username=request.POST["activate"])
                Token(user=user).save()
            except User.DoesNotExist:
                pass
        elif "token" in request.POST:
            try:
                user = User.objects.get(username=request.POST["token"])
                Token.objects.get(user=user).delete()
            except (User.DoesNotExist, Token.DoesNotExist):
                pass
        elif "renew" in request.POST:
            try:
                user = User.objects.get(username=request.POST["token"])
                Token.objects.get(user=user).delete()
                Token(user=user).save()
            except (User.DoesNotExist, Token.DoesNotExist):
                pass
        else:
            users = User.objects.exclude(is_superuser=True).order_by("last_name")
            users = users.filter(Q(first_name__icontains=request.POST["search"]) | Q(last_name__icontains=request.POST["search"])).order_by("last_name")

            match(request.POST["type"]):
                case "a":
                    users = users.exclude(is_active=False)
                case "au":
                    users = users.exclude(Q(groups__name__in="Trainers__in") and Q(is_active=False))
                case "at":
                    users = users.filter(Q(groups__name="Trainers") and Q(is_active=True))
                case "i":
                    users = users.filter(is_active=False)
                case "iu":
                    users = users.exclude(Q(groups__name__in="Trainers") and Q(is_active=True))
                case "it":
                    users = users.filter(Q(groups__name__in="Trainers") and Q(is_active=False))

            return render(request, "htmx/users.html", {"users": users})

        return HttpResponseRedirect("")
    else:
        return render(request, "manage_users.html")


@user_passes_test(is_admin)
def new_user(request):
    if request.method == "POST":
        group, created = Group.objects.get_or_create(name="Trainers")
        newusername = unique_username(request.POST["first_name"] + "." + request.POST["last_name"])
        newuser = User(
            username=newusername,
            first_name=request.POST["first_name"],
            last_name=request.POST["last_name"],
            is_active=False
        )
        newuser.save()
        newuser.groups.add(group)
        Token(user=newuser).save()

    return render(request, "new_user.html", {})
