from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from guardian.shortcuts import assign_perm, get_objects_for_user
from guardian.decorators import permission_required as object_permission_required
import json

from .models import Fighter, OwnTechnique, Technique, Position


# Create your views here.
def index(request):
    shown_profiles = get_objects_for_user(request.user, "view_fighter", Fighter)
    return render(request, "index.html", {"profiles": shown_profiles})


@object_permission_required("main.change_fighter", (Fighter, "id", "profile_id"))
def edit_profile(request, profile_id):
    if request.method == "POST":
        data = json.loads(request.body)

        fighter = Fighter.objects.get(id=profile_id)

        if data["action"] == "delete":
            fighter.delete()

            return HttpResponseRedirect("/")
        else:
            # fighter
            fighter.name = data["name"]
            fighter.last_name = data["last_name"]
            fighter.year = data["year"]
            fighter.weight = data["weight"]
            fighter.primary_side = data["side"]
            fighter.save()

            # own_techniques
            for own_technique in data["own_techniques"]:
                match own_technique["action"]:
                    case "add":
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
                    case "update":
                        changed_own_technique = OwnTechnique.objects.get(id=own_technique["id"])
                        changed_own_technique.side = own_technique["side"]
                        changed_own_technique.state = own_technique["state"]
                        changed_own_technique.direction = own_technique["direction"]
                        changed_own_technique.fighter_profile = fighter
                        changed_own_technique.technique = Technique.objects.get(id=own_technique["technique"])
                        changed_own_technique.left_position = Position.objects.get(fighter_profile=fighter, side=True, number=own_technique["left"])
                        changed_own_technique.right_position = Position.objects.get(fighter_profile=fighter, side=False, number=own_technique["right"])
                        changed_own_technique.save()
                    case "delete":
                        OwnTechnique.objects.get(id=own_technique["id"]).delete()

            # positions
            for position in data["positions"]:
                match position["action"]:
                    case "add":
                        new_position = Position(
                            number=position["number"],
                            side=position["side"],
                            x=position["x"],
                            y=position["y"],
                            fighter_profile=fighter
                        )
                        new_position.save()
                    case "update":
                        changed_position = Position.objects.get(id=position["id"])
                        changed_position.number = position["number"]
                        changed_position.side = position["side"]
                        changed_position.x = position["x"]
                        changed_position.y = position["y"]
                        changed_position.fighter_profile = fighter
                        changed_position.save()
                    case "delete":
                        Position.objects.get(id=position["id"]).delete()

            if data["action"] == "save":

                return HttpResponseRedirect("/" + str(fighter.id) + "/edit")

            else:

                return HttpResponseRedirect("/" + str(fighter.id))

    else:
        fighter = Fighter.objects.get(id=profile_id)
        own_techniques = OwnTechnique.objects.filter(fighter_profile=fighter)
        techniques = Technique.objects.filter(type="S").order_by("name")
        positions = Position.objects.filter(fighter_profile=fighter)

        return render(request, "edit.html", {"fighter": fighter, "own_techniques": own_techniques, "techniques": techniques, "positions": positions})


@object_permission_required("main.view_fighter", (Fighter, "id", "profile_id"))
def profile(request, profile_id):
    fighter = Fighter.objects.get(id=profile_id)
    own_techniques = OwnTechnique.objects.filter(fighter_profile=fighter)
    positons = Position.objects.filter(fighter_profile=fighter)
    return render(request, "profile.html", {"fighter": fighter, "own_techniques": own_techniques, "positions": positons})


@permission_required("main.add_fighter")
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
