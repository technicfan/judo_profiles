from django.shortcuts import render, HttpResponse
from django.db.models import Q
from . models import Fighter, OwnTechnique, SpecialTechnique

# Create your views here.
def index(request):
    shown_profiles = Fighter.objects.filter(Q(created_by=request.user) | Q(can_be_seen_by=request.user))
    return render(request, "index.html", {"profiles": shown_profiles})

def edit_profile(request, profile_id):
    if request.method == "POST":
        return
    else:
        fighter = Fighter.objects.get(id=profile_id)
        techniques = SpecialTechnique.objects.filter(fighter_profile=fighter).order_by("number")
        return render(request, "edit.html", {"fighter": fighter, "techniques": techniques})

def profile(request, profile_id):
    fighter = Fighter.objects.get(id=profile_id)
    techniques = SpecialTechnique.objects.filter(fighter_profile=fighter).order_by("number")
    return render(request, "profile.html", {"fighter": fighter, "techniques": techniques})