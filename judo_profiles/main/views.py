from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.db.models import Q
import json

from .models import Fighter, OwnTechnique, TechniqueRank, Technique, Position

# Create your views here.
def index(request):
    #shown_profiles = Fighter.objects.filter(Q(created_by=request.user) | Q(can_be_seen_by=request.user))
    #return render(request, "index.html", {"profiles": shown_profiles})
    return HttpResponse("test")

def edit_profile(request, profile_id):
    if request.method == "POST":
        return
    else:
        fighter = Fighter.objects.get(id=profile_id)
        own = OwnTechnique.objects.filter(fighter_profile=fighter)
        best = TechniqueRank.objects.filter(fighter_profile=fighter).order_by("number")
        techniques = Technique.objects.all()
        return render(request, "edit.html", {"fighter": fighter, "best": best, "own": own, "techniques": techniques})

def profile(request, profile_id):
    fighter = Fighter.objects.get(id=profile_id)
    techniques = TechniqueRank.objects.filter(fighter_profile=fighter).order_by("number")
    return render(request, "profile.html", {"fighter": fighter, "techniques": techniques})

def new_profile(request):
    if request.method == "POST":
        data = json.loads(request.body)
        fighter = Fighter()
        fighter.name = data["name"]
        fighter.last_name = data["last_name"]
        fighter.year = data["year"]
        fighter.weight = data["weight"]
        fighter.primary_side = data["side"]
        fighter.save()

        for position in data["positions"]:
            new_position = Position()
            new_position.number = position["number"]
            new_position.side = position["side"]
            new_position.x = position["x"]
            new_position.y = position["y"]
            new_position.fighter_profile = fighter
            new_position.save()

        for own_technique in data["own_techniques"]:
            new_own_technique = OwnTechnique()
            new_own_technique.side = own_technique["side"]
            new_own_technique.state = own_technique["state"]
            new_own_technique.direction = own_technique["direction"]
            new_own_technique.fighter_profile = fighter
            new_own_technique.technique = Technique.objects.get(id=own_technique["technique"])
            new_own_technique.left_position = Position.objects.get(fighter_profile=fighter, side=True, number=own_technique["left"])
            new_own_technique.right_position = Position.objects.get(fighter_profile=fighter, side=False, number=own_technique["right"])
            new_own_technique.save()

        return HttpResponseRedirect("/" + str(fighter.id))
    else:
        techniques = Technique.objects.filter(type="S").order_by("name")
        return render(request, "new.html", {"techniques": techniques})