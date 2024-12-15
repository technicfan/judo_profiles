from django.shortcuts import render, HttpResponse
from django.db.models import Q
from . models import Fighter

# Create your views here.
def index(request):
    shown_profiles = Fighter.objects.filter(Q(created_by=request.user) | Q(can_be_seen_by=request.user))
    return HttpResponse(shown_profiles)

def edit_profile(request, profile_id):
    if request.method == "POST":
        return
    else:
        fighter = Fighter.objects.get(id=profile_id)
        return render(request, "edit.html", {"name": fighter.name, "last_name": fighter.last_name})