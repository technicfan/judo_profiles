from django.shortcuts import render, HttpResponseRedirect
from guardian.shortcuts import assign_perm, get_objects_for_user
import json

from .models import Fighter, OwnTechnique, TechniqueRank, Technique, Position


# Create your views here.
def index(request):
    shown_profiles = get_objects_for_user(request.user, "view_fighter", Fighter)
    return render(request, "index.html", {"profiles": shown_profiles})


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
    best = TechniqueRank.objects.filter(fighter_profile=fighter).order_by("number")
    own_techniques = OwnTechnique.objects.filter(fighter_profile=fighter)
    positons = Position.objects.filter(fighter_profile=fighter)
    return render(request, "profile.html", {"fighter": fighter, "best": best, "own_techniques": own_techniques, "positions": positons})


def new_profile(request):
    if request.method == "POST":
        data = json.loads(request.body)
        fighter = Fighter(
            name=data["name"],
            last_name=data["last_name"],
            year=data["year"],
            weight=data["weight"],
            primary_side=data["side"]
        )
        fighter.save()
        assign_perm('change_fighter', request.user, fighter)
        assign_perm('view_fighter', request.user, fighter)
        assign_perm('manage_fighter', request.user, fighter)

        for position in data["positions"]:
            new_position = Position(
                number=position["number"],
                side=position["side"],
                x=position["x"],
                y=position["y"],
                fighter_profile=fighter
            )
            new_position.save()
            # assign_perm('change_position', request.user, new_position)
            # assign_perm('view_position', request.user, new_position)

        for own_technique in data["own_techniques"]:
            new_own_technique = OwnTechnique(
                side=own_technique["side"],
                state=own_technique["state"],
                direction=own_technique["direction"],
                fighter_profile=fighter,
                technique=Technique.objects.get(id=own_technique["technique"]),
                left_position=Position.objects.get(fighter_profile=fighter, side=True, number=own_technique["left"]),
                right_position=Position.objects.get(fighter_profile=fighter, side=False, number=own_technique["right"])
            )
            new_own_technique.save()
            # assign_perm('change_own_position', request.user, new_own_technique)
            # assign_perm('view_own_position', request.user, new_own_technique)

        return HttpResponseRedirect("/" + str(fighter.id))
    else:
        techniques = Technique.objects.filter(type="S").order_by("name")
        return render(request, "new.html", {"techniques": techniques})
