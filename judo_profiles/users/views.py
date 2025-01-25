from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.models import User


@login_not_required
def auth(request):
    next = request.GET.get("next")
    if request.method == "POST":
        user = authenticate(request, username=request.POST["user"], password=request.POST["pass"])
        if user is not None:
            login(request, user)

            return HttpResponseRedirect(next)
        else:
            return render(request, "login.html", {"next": next})
    else:
        return render(request, "login.html", {"next": next})


def change_pass(request):
    if request.method == "POST":
        user = authenticate(request, username=request.POST["user"], password=request.POST["pass"])
        if user == request.user and request.POST["new_pass"] == request.POST["new_pass_confirm"]:
            request.user.set_password(request.POST["new_pass"])
            request.user.save()
            logout(request)

            return HttpResponseRedirect("")
        else:
            return render(request, "change_pass.html")
    else: 
        return render(request, "change_pass.html")
