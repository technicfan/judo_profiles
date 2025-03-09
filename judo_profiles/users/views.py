from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.models import User  # , Permission, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required

from .models import Token


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
                return render(request, "register.html", {})
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
                return render(request, "register.html", {})
        else:
            return render(request, "register.html", {})
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
