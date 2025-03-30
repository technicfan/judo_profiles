from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import permission_required, login_not_required
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm
from guardian.decorators import permission_required as object_permission_required
import json

from .models import Profile, OwnTechnique, Technique, Position, CombinationRank, TechniqueRank
from users.models import Token


def unique_username(username: str) -> str:
    number = User.objects.filter(username__regex=rf"^{username}(\.[0-9]*)?$").count()
    if number != 0:
        return f"{username}_{number}"
    else:
        return username


@login_not_required
def home(request):
    if request.user.is_authenticated:
        return redirect("profiles-profiles")
    else:
        return redirect("profiles-about")


@login_not_required
def about(request):
    return render(request, "about.html")


def start(request):
    if request.method == "POST":
        shown_profiles = get_objects_for_user(request.user, "view_profile", Profile).order_by("last_name")
        search = request.POST["search"]
        filtered = shown_profiles.filter(Q(name__icontains=search) | Q(last_name__icontains=search))

        return render(request, "htmx/profiles.html", {"profiles": filtered})
    else:

        return render(request, "profiles.html")


@permission_required("profiles.add_profile")
def new_profile(request):
    if request.method == "POST":
        data = json.loads(request.body)
        profile = Profile(
            name=data["name"],
            last_name=data["last_name"],
            year=data["year"],
            weight=data["weight"],
            primary_side=data["side"],
            created_by=request.user
        )
        username = unique_username(profile.name + "." + profile.last_name)
        newuser = User(
            username=username,
            first_name=profile.name,
            last_name=profile.last_name,
            is_active=False
        )
        newuser.save()
        profile.user = newuser
        profile.save()
        assign_perm("view_profile", newuser, profile)
        assign_perm('view_profile', request.user, profile)
        assign_perm('change_profile', request.user, profile)
        assign_perm('manage_profile', request.user, profile)

        for position in data["positions"]:
            new_position = Position(
                number=position["number"],
                side=position["side"],
                x=position["x"],
                y=position["y"],
                profile=profile
            )
            new_position.save()

        for own_technique in data["own_techniques"]:
            new_own_technique = OwnTechnique(
                side=own_technique["side"],
                state=own_technique["state"],
                direction=own_technique["direction"],
                profile=profile,
                technique=Technique.objects.get(id=own_technique["technique"]),
                left_position=Position.objects.get(profile=profile, side=True, number=own_technique["left"]),
                right_position=Position.objects.get(profile=profile, side=False, number=own_technique["right"])
            )
            new_own_technique.save()

        for rank_item in data["rank_items"]:
            if rank_item["type"] == "combination":
                new_rank_item = CombinationRank(
                    number=rank_item["number"],
                    technique1=Technique.objects.get(id=rank_item["technique1"]),
                    technique2=Technique.objects.get(id=rank_item["technique2"]),
                    profile=profile
                )
            else:
                new_rank_item = TechniqueRank(
                    number=rank_item["number"],
                    technique=Technique.objects.get(id=rank_item["technique"]),
                    profile=profile,
                    type=rank_item["type"]
                )
            new_rank_item.save()

        return redirect("profiles-profile", username=profile.user.username)
    else:
        stechniques = Technique.objects.filter(type="S").order_by("name")
        gtechniques = Technique.objects.filter(type="B").order_by("name")
        techniques = Technique.objects.all().order_by("name")

        return render(request, "profiles/new.html", {"techniques": techniques, "stechniques": stechniques, "gtechniques": gtechniques})


@object_permission_required("profiles.view_profile", (Profile, "user__username", "username"))
def profile(request, username):
    profile = User.objects.get(username=username).profile
    own_techniques = OwnTechnique.objects.filter(profile=profile)
    positons = Position.objects.filter(profile=profile)
    special_rank = TechniqueRank.objects.filter(profile=profile, type="special").order_by("number")
    ground_rank = TechniqueRank.objects.filter(profile=profile, type="ground").order_by("number")
    combination_rank = CombinationRank.objects.filter(profile=profile).order_by("number")
    return render(request, "profiles/profile.html", {
        "profile": profile,
        "own_techniques": own_techniques,
        "positions": positons,
        "special_rank": special_rank,
        "ground_rank": ground_rank,
        "combination_rank": combination_rank
    })


@object_permission_required("profiles.change_profile", (Profile, "user__username", "username"))
def edit_profile(request, username):
    if request.method == "POST":
        data = json.loads(request.body)

        profile = User.objects.get(username=username).profile

        if data["action"] == "delete" and request.user == profile.created_by:
            profile.delete()

            return redirect("profiles-profiles")
        else:
            # profile
            profile.name = data["name"]
            profile.last_name = data["last_name"]
            profile.year = data["year"]
            profile.weight = data["weight"]
            profile.primary_side = data["side"]
            profile.save()

            # positions
            for position in data["positions"]:
                match position["action"]:
                    case "add":
                        new_position = Position(
                            number=position["number"],
                            side=position["side"],
                            x=position["x"],
                            y=position["y"],
                            profile=profile
                        )
                        new_position.save()
                    case "update":
                        changed_position = Position.objects.get(id=position["id"])
                        if changed_position.profile == profile:
                            changed_position.number = position["number"]
                            changed_position.side = position["side"]
                            changed_position.x = position["x"]
                            changed_position.y = position["y"]
                            changed_position.profile = profile
                            changed_position.save()
                    case "delete":
                        to_be_deleted = Position.objects.get(id=position["id"])
                        if to_be_deleted.profile == profile:
                            to_be_deleted.delete()

            # own_techniques
            for own_technique in data["own_techniques"]:
                match own_technique["action"]:
                    case "add":
                        new_own_technique = OwnTechnique(
                            side=own_technique["side"],
                            state=own_technique["state"],
                            direction=own_technique["direction"],
                            profile=profile,
                            technique=Technique.objects.get(id=own_technique["technique"]),
                            left_position=Position.objects.get(profile=profile, side=True, number=own_technique["left"]),
                            right_position=Position.objects.get(profile=profile, side=False, number=own_technique["right"])
                        )
                        new_own_technique.save()
                    case "update":
                        changed_own_technique = OwnTechnique.objects.get(id=own_technique["id"])
                        if changed_position.profile == profile:
                            changed_own_technique.side = own_technique["side"]
                            changed_own_technique.state = own_technique["state"]
                            changed_own_technique.direction = own_technique["direction"]
                            changed_own_technique.profile = profile
                            changed_own_technique.technique = Technique.objects.get(id=own_technique["technique"])
                            changed_own_technique.left_position = Position.objects.get(profile=profile, side=True, number=own_technique["left"])
                            changed_own_technique.right_position = Position.objects.get(profile=profile, side=False, number=own_technique["right"])
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
                                profile=profile
                            )
                        else:
                            new_rank_item = TechniqueRank(
                                number=rank_item["number"],
                                technique=Technique.objects.get(id=rank_item["technique"]),
                                profile=profile,
                                type=rank_item["type"]
                            )
                        new_rank_item.save()
                    case "update":
                        if rank_item["type"] == "combination":
                            changed_rank_item = CombinationRank.objects.get(id=rank_item["id"])
                            changed_rank_item.number = rank_item["number"]
                            changed_rank_item.technique1 = Technique.objects.get(id=rank_item["technique1"])
                            changed_rank_item.technique2 = Technique.objects.get(id=rank_item["technique2"])
                            changed_rank_item.profile = profile
                        else:
                            changed_rank_item = TechniqueRank.objects.get(id=rank_item["id"])
                            changed_rank_item.number = rank_item["number"]
                            changed_rank_item.technique = Technique.objects.get(id=rank_item["technique"])
                            changed_rank_item.profile = profile
                            changed_rank_item.type = rank_item["type"]
                        if changed_rank_item.profile == profile:
                            changed_rank_item.save()
                    case "delete":
                        if rank_item["type"] == "combination":
                            to_be_deleted = CombinationRank.objects.get(id=rank_item["id"])
                        else:
                            to_be_deleted = TechniqueRank.objects.get(id=rank_item["id"])
                        if to_be_deleted.profile == profile:
                            to_be_deleted.delete()

            if data["action"] == "save":

                return redirect("profiles-profile-edit", username=profile.user.username)

            else:

                return redirect("profiles-profile", username=profile.user.username)

    else:
        profile = User.objects.get(username=username).profile
        own_techniques = OwnTechnique.objects.filter(profile=profile)
        stechniques = Technique.objects.filter(type="S").order_by("name")
        gtechniques = Technique.objects.filter(type="B").order_by("name")
        techniques = Technique.objects.all().order_by("name")
        positions = Position.objects.filter(profile=profile)
        technique_ranks = TechniqueRank.objects.filter(profile=profile).order_by("number")
        combination_rank = CombinationRank.objects.filter(profile=profile).order_by("number")

        return render(request, "profiles/edit.html", {
            "profile": profile,
            "own_techniques": own_techniques,
            "stechniques": stechniques,
            "gtechniques": gtechniques,
            "techniques": techniques,
            "positions": positions,
            "technique_ranks": technique_ranks,
            "combination_rank": combination_rank
        })


@object_permission_required("profiles.change_profile", (Profile, "user__username", "username"))
def manage_profile(request, username):
    profile = User.objects.get(username=username).profile
    users = User.objects.exclude(
        Q(is_superuser=True) | Q(id__in=[request.user.id, profile.created_by.id]) | Q(is_active=False)
    ).order_by("username")

    if request.method == "POST":
        if "add" in request.POST:
            Token(user=profile.user).save()
        elif "renew" in request.POST:
            user = profile.user
            user.token.delete()
            Token(user=user).save()
        elif "delete_token" in request.POST:
            profile.user.token.delete()
        elif "delete_user" in request.POST:
            profile.user.is_active = False
            profile.user.set_unusable_password()
            profile.user.save()
        elif "update" in request.POST:
            permission = request.POST["permission"]
            permissions = [
                "view_profile",
                "change_profile",
                "manage_profile"
            ]
            remove = users
            for id in request.POST:
                if id.isdigit():
                    try:
                        user = User.objects.get(id=int(id))
                        for p in permissions[:permissions.index(permission) + 1]:
                            assign_perm(p, user, profile)
                        remove = remove.exclude(id=int(id))
                    except (User.DoesNotExist, ValueError):
                        pass

            for user in remove:
                for p in permissions[permissions.index(permission):]:
                    remove_perm(p, user, profile)

            return HttpResponse("Gespeichert")
        elif "search" in request.POST:
            search = request.POST["search"]
            permission = request.POST["permission"]
            if permission == "view_profile":
                if profile.user:
                    users = users.exclude(id=profile.user.id)
            else:
                users = users.filter(groups__name="Trainers")
            filtered = users.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search))
            if filtered.count() == 0:
                filtered = None

            return render(request, "htmx/profile_permissions.html", {"users": filtered, "profile": profile, "permission": permission})

        return redirect("profiles-profile-manage", username=username)
    else:

        return render(request, "profiles/manage.html", {"profile": profile})
