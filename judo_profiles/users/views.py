from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_not_required

# Create your views here.
@login_not_required
def auth(request):
    if request.method == "POST":
        user = authenticate(request, username=request.POST["user"], password=request.POST["pass"])
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(request.GET.get('next'))
        else:
            return render(request, "login.html")
    else:
        return render(request, "login.html")
