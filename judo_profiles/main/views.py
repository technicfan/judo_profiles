from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm, get_users_with_perms
from guardian.decorators import permission_required as object_permission_required
import json

from .models import Fighter, OwnTechnique, Technique, Position, CombinationRank, TechniqueRank


def index(request):
    shown_profiles = get_objects_for_user(request.user, "view_fighter", Fighter).order_by("last_name")
    return render(request, "index.html", {"profiles": shown_profiles})


@object_permission_required("main.change_fighter", (Fighter, "uuid", "profile_uuid"))
def edit_profile(request, profile_uuid):
    if request.method == "POST":
        data = json.loads(request.body)

        fighter = Fighter.objects.get(uuid=profile_uuid)

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
                        if changed_position.fighter_profile == fighter:
                            changed_position.number = position["number"]
                            changed_position.side = position["side"]
                            changed_position.x = position["x"]
                            changed_position.y = position["y"]
                            changed_position.fighter_profile = fighter
                            changed_position.save()
                    case "delete":
                        to_be_deleted = Position.objects.get(id=position["id"])
                        if to_be_deleted.fighter_profile == fighter:
                            to_be_deleted.delete()

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
                        if changed_position.fighter_profile == fighter:
                            changed_own_technique.side = own_technique["side"]
                            changed_own_technique.state = own_technique["state"]
                            changed_own_technique.direction = own_technique["direction"]
                            changed_own_technique.fighter_profile = fighter
                            changed_own_technique.technique = Technique.objects.get(id=own_technique["technique"])
                            changed_own_technique.left_position = Position.objects.get(fighter_profile=fighter, side=True, number=own_technique["left"])
                            changed_own_technique.right_position = Position.objects.get(fighter_profile=fighter, side=False, number=own_technique["right"])
                            changed_own_technique.save()
                    case "delete":
                        to_be_deleted = OwnTechnique.objects.get(id=own_technique["id"])
                        to_be_deleted.delete()

            for rank_item in data["rank_items"]:
                match rank_item["action"]:
                    case "add":
                        if rank_item["type"] == "combination":
                            new_rank_item = CombinationRank(
                                number=rank_item["number"],
                                technique1=Technique.objects.get(id=rank_item["technique1"]),
                                technique2=Technique.objects.get(id=rank_item["technique2"]),
                                fighter_profile=fighter
                            )
                        else:
                            new_rank_item = TechniqueRank(
                                number=rank_item["number"],
                                technique=Technique.objects.get(id=rank_item["technique"]),
                                fighter_profile=fighter,
                                type=rank_item["type"]
                            )
                        new_rank_item.save()
                    case "update":
                        if rank_item["type"] == "combination":
                            changed_rank_item = CombinationRank.objects.get(id=rank_item["id"])
                            changed_rank_item.number = rank_item["number"]
                            changed_rank_item.technique1 = Technique.objects.get(id=rank_item["technique1"])
                            changed_rank_item.technique2 = Technique.objects.get(id=rank_item["technique2"])
                            changed_rank_item.fighter_profile = fighter
                        else:
                            changed_rank_item = TechniqueRank.objects.get(id=rank_item["id"])
                            changed_rank_item.number = rank_item["number"]
                            changed_rank_item.technique = Technique.objects.get(id=rank_item["technique"])
                            changed_rank_item.fighter_profile = fighter
                            changed_rank_item.type = rank_item["type"]
                        if changed_rank_item.fighter_profile == fighter:
                            changed_rank_item.save()
                    case "delete":
                        if rank_item["type"] == "combination":
                            to_be_deleted = CombinationRank.objects.get(id=rank_item["id"])
                        else:
                            to_be_deleted = TechniqueRank.objects.get(id=rank_item["id"])
                        if to_be_deleted.fighter_profile == fighter:
                            to_be_deleted.delete()

            if data["action"] == "save":

                return HttpResponseRedirect(request.path)

            else:

                return HttpResponseRedirect("/".join(request.path.split("/")[:-1]))

    else:
        fighter = Fighter.objects.get(uuid=profile_uuid)
        own_techniques = OwnTechnique.objects.filter(fighter_profile=fighter)
        stechniques = Technique.objects.filter(type="S").order_by("name")
        gtechniques = Technique.objects.filter(type="B").order_by("name")
        techniques = Technique.objects.all().order_by("name")
        positions = Position.objects.filter(fighter_profile=fighter)
        technique_ranks = TechniqueRank.objects.filter(fighter_profile=fighter).order_by("number")
        combination_rank = CombinationRank.objects.filter(fighter_profile=fighter).order_by("number")

        return render(request, "edit.html", {
            "fighter": fighter,
            "own_techniques": own_techniques,
            "stechniques": stechniques,
            "gtechniques": gtechniques,
            "techniques": techniques,
            "positions": positions,
            "technique_ranks": technique_ranks,
            "combination_rank": combination_rank
        })


@object_permission_required("main.view_fighter", (Fighter, "uuid", "profile_uuid"))
def profile(request, profile_uuid):
    fighter = Fighter.objects.get(uuid=profile_uuid)
    own_techniques = OwnTechnique.objects.filter(fighter_profile=fighter)
    positons = Position.objects.filter(fighter_profile=fighter)
    special_rank = TechniqueRank.objects.filter(fighter_profile=fighter, type="special").order_by("number")
    ground_rank = TechniqueRank.objects.filter(fighter_profile=fighter, type="ground").order_by("number")
    combination_rank = CombinationRank.objects.filter(fighter_profile=fighter).order_by("number")
    return render(request, "profile.html", {
        "fighter": fighter,
        "own_techniques": own_techniques,
        "positions": positons,
        "special_rank": special_rank,
        "ground_rank": ground_rank,
        "combination_rank": combination_rank
    })


@permission_required("main.add_fighter")
def new_profile(request):
    if request.method == "POST":
        data = json.loads(request.body)
        fighter = Fighter(
            name=data["name"],
            last_name=data["last_name"],
            year=data["year"],
            weight=data["weight"],
            primary_side=data["side"],
            created_by=request.user
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

        for rank_item in data["rank_items"]:
            if rank_item["type"] == "combination":
                new_rank_item = CombinationRank(
                    number=rank_item["number"],
                    technique1=Technique.objects.get(id=rank_item["technique1"]),
                    technique2=Technique.objects.get(id=rank_item["technique2"]),
                    fighter_profile=fighter
                )
            else:
                new_rank_item = TechniqueRank(
                    number=rank_item["number"],
                    technique=Technique.objects.get(id=rank_item["technique"]),
                    fighter_profile=fighter,
                    type=rank_item["type"]
                )
            new_rank_item.save()

        return HttpResponseRedirect("/profile/" + str(fighter.uuid))
    else:
        stechniques = Technique.objects.filter(type="S").order_by("name")
        gtechniques = Technique.objects.filter(type="B").order_by("name")
        techniques = Technique.objects.all().order_by("name")

        return render(request, "new.html", {"techniques": techniques, "stechniques": stechniques, "gtechniques": gtechniques})


@object_permission_required("main.manage_fighter", (Fighter, "uuid", "profile_uuid"))
def manage(request, profile_uuid):
    fighter = Fighter.objects.get(uuid=profile_uuid)
    users = User.objects.exclude(id__in=[request.user.id, fighter.created_by.id]).order_by("username")

    if request.method == "POST":
        if "password" in request.POST:
            if request.POST["password"] == request.POST["password_confirm"]:
                username = fighter.name + "." + fighter.last_name
                number = User.objects.filter(username__regex=rf"^{username}(\.[0-9]*)?$").count()
                if number != 0:
                    username += f".{number}"
                newuser = User(username=username)
                newuser.set_password(request.POST["password"])
                newuser.save()
                assign_perm('view_fighter', newuser, fighter)
                fighter.user = newuser
                fighter.save()
        elif "delete" in request.POST:
            fighter.user.delete()
        else:
            no_view = users
            no_edit = users
            no_manage = users

            if "view_users" in request.POST:
                for username in request.POST.getlist("view_users"):
                    user = User.objects.get(username=username)
                    assign_perm('view_fighter', user, fighter)
                    no_view = no_view.exclude(username=username)

            if "edit_users" in request.POST:
                for username in request.POST.getlist("edit_users"):
                    user = User.objects.get(username=username)
                    assign_perm('view_fighter', user, fighter)
                    assign_perm('change_fighter', user, fighter)
                    no_edit = no_edit.exclude(username=username)

            if "manage_users" in request.POST:
                for username in request.POST.getlist("manage_users"):
                    user = User.objects.get(username=username)
                    assign_perm('view_fighter', user, fighter)
                    assign_perm('change_fighter', user, fighter)
                    assign_perm('manage_fighter', user, fighter)
                    no_manage = no_manage.exclude(username=username)

            for user in no_view:
                if user in no_edit and user in no_manage and user != fighter.user:
                    remove_perm('view_fighter', user, fighter)

            for user in no_edit:
                if user in no_manage:
                    remove_perm('change_fighter', user, fighter)

            for user in no_manage:
                remove_perm('manage_fighter', user, fighter)

        return HttpResponseRedirect("")
    else:

        return render(request, "manage.html", {"users": users, "fighter": fighter})
