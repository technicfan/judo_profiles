import json

from django.conf import settings
from django.contrib.auth.decorators import login_not_required, permission_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from guardian.decorators import permission_required as object_permission_required
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm

from judo_profiles.models import (
    CombinationRank,
    OwnTechnique,
    Position,
    Profile,
    Technique,
    TechniqueRank,
    Token,
)


# create unique username for new user
def unique_username(username: str) -> str:
    # check how often initial name already exists
    number = User.objects.filter(username__regex=rf"^{username}(_[0-9]*)?$").count()
    # return unique username
    if number != 0:
        return f"{username}_{number}"
    else:
        return username


# landing page for non authorized and authorized users
@login_not_required
def home(request):
    if request.user.is_authenticated:
        return redirect("profiles-profiles")
    else:
        return redirect("profiles-about")


@login_not_required
def about(request):
    print(request.LANGUAGE_CODE)
    print(settings.LANGUAGE_CODE)
    try:
        template = get_template(f"lang/{request.LANGUAGE_CODE}/about.html")
    except TemplateDoesNotExist:
        template = get_template(f"lang/{settings.LANGUAGE_CODE}/about.html")
    return HttpResponse(template.render({}, request))


# list all available profiles
def start(request):
    if request.method == "POST":
        # get profiles with search
        shown_profiles = get_objects_for_user(
            request.user, "view_profile", Profile
        ).order_by("last_name")
        search = request.POST["search"]
        filtered = shown_profiles.filter(
            Q(name__icontains=search) | Q(last_name__icontains=search)
        )

        # return html table for htmx
        return render(request, "htmx/profiles.html", {"profiles": filtered})
    else:
        # return template
        return render(request, "profiles.html")


@permission_required("profiles.add_profile")
def new_profile(request):
    if request.method == "POST":
        data = json.loads(request.body)
        # general data
        profile = Profile(
            name=data["name"],
            last_name=data["last_name"],
            year=data["year"],
            weight=data["weight"],
            primary_side=data["side"],
            created_by=request.user,
        )
        # create new user for profile
        username = unique_username(profile.name + "." + profile.last_name)
        newuser = User(
            username=username,
            first_name=profile.name,
            last_name=profile.last_name,
            is_active=False,
        )
        newuser.save()
        profile.user = newuser
        profile.save()
        # permissions
        assign_perm("view_profile", newuser, profile)
        assign_perm("view_profile", request.user, profile)
        assign_perm("change_profile", request.user, profile)
        assign_perm("manage_profile", request.user, profile)

        # positions
        for position in data["positions"]:
            new_position = Position(
                number=position["number"],
                side=position["side"],
                x=position["x"],
                y=position["y"],
                profile=profile,
            )
            new_position.save()

        # own techniques
        for own_technique in data["own_techniques"]:
            new_own_technique = OwnTechnique(
                side=own_technique["side"],
                state=own_technique["state"],
                direction=own_technique["direction"],
                profile=profile,
                technique=Technique.objects.get(id=own_technique["technique"]),
                left_position=Position.objects.get(
                    profile=profile, side=True, number=own_technique["left"]
                ),
                right_position=Position.objects.get(
                    profile=profile, side=False, number=own_technique["right"]
                ),
            )
            new_own_technique.save()

        # ranks
        for rank_item in data["rank_items"]:
            # combination or single technique
            if rank_item["type"] == "combination":
                new_rank_item = CombinationRank(
                    number=rank_item["number"],
                    technique1=Technique.objects.get(id=rank_item["technique1"]),
                    technique2=Technique.objects.get(id=rank_item["technique2"]),
                    profile=profile,
                )
            else:
                new_rank_item = TechniqueRank(
                    number=rank_item["number"],
                    technique=Technique.objects.get(id=rank_item["technique"]),
                    profile=profile,
                    type=rank_item["type"] == "special",
                )
            new_rank_item.save()

        # redirect to created profile
        return redirect("profiles-profile", username=profile.user.username)
    else:
        stechniques = Technique.objects.filter(type="S").order_by("name")
        gtechniques = Technique.objects.filter(type="B").order_by("name")
        techniques = Technique.objects.all().order_by("name")

        # return template with techniques
        return render(
            request,
            "profiles/new.html",
            {
                "techniques": techniques,
                "stechniques": stechniques,
                "gtechniques": gtechniques,
            },
        )


@object_permission_required(
    "profiles.view_profile", (Profile, "user__username", "username")
)
def profile(request, username):
    # collect profile data
    profile = User.objects.get(username=username).profile
    own_techniques = OwnTechnique.objects.filter(profile=profile)
    positons = Position.objects.filter(profile=profile)
    special_rank = TechniqueRank.objects.filter(profile=profile, type=1).order_by(
        "number"
    )
    ground_rank = TechniqueRank.objects.filter(profile=profile, type=0).order_by(
        "number"
    )
    combination_rank = CombinationRank.objects.filter(profile=profile).order_by(
        "number"
    )

    # return template with profile data
    return render(
        request,
        "profiles/profile.html",
        {
            "profile": profile,
            "own_techniques": own_techniques,
            "positions": positons,
            "special_rank": special_rank,
            "ground_rank": ground_rank,
            "combination_rank": combination_rank,
        },
    )


@object_permission_required(
    "profiles.change_profile", (Profile, "user__username", "username")
)
def edit_profile(request, username):
    if request.method == "POST":
        data = json.loads(request.body)

        profile = User.objects.get(username=username).profile

        if data["action"] == "delete" and request.user == profile.created_by:
            # delete profile and inactive user
            if profile.user.is_active:
                profile.delete()
            else:
                profile.user.delete()

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
                    # create new position
                    case "add":
                        new_position = Position(
                            number=position["number"],
                            side=position["side"],
                            x=position["x"],
                            y=position["y"],
                            profile=profile,
                        )
                        new_position.save()
                    # update position if profile matches
                    case "update":
                        changed_position = Position.objects.get(id=position["id"])
                        if changed_position.profile == profile:
                            changed_position.number = position["number"]
                            changed_position.side = position["side"]
                            changed_position.x = position["x"]
                            changed_position.y = position["y"]
                            changed_position.save()
                    # delete position if profile matches
                    case "delete":
                        to_be_deleted = Position.objects.get(id=position["id"])
                        if to_be_deleted.profile == profile:
                            to_be_deleted.delete()

            # own_techniques
            for own_technique in data["own_techniques"]:
                match own_technique["action"]:
                    # create new own technique
                    case "add":
                        new_own_technique = OwnTechnique(
                            side=own_technique["side"],
                            state=own_technique["state"],
                            direction=own_technique["direction"],
                            profile=profile,
                            technique=Technique.objects.get(
                                id=own_technique["technique"]
                            ),
                            left_position=Position.objects.get(
                                profile=profile, side=True, number=own_technique["left"]
                            ),
                            right_position=Position.objects.get(
                                profile=profile,
                                side=False,
                                number=own_technique["right"],
                            ),
                        )
                        new_own_technique.save()
                    # update own technique if profile matches
                    case "update":
                        changed_own_technique = OwnTechnique.objects.get(
                            id=own_technique["id"]
                        )
                        if changed_own_technique.profile == profile:
                            changed_own_technique.side = own_technique["side"]
                            changed_own_technique.state = own_technique["state"]
                            changed_own_technique.direction = own_technique["direction"]
                            changed_own_technique.technique = Technique.objects.get(
                                id=own_technique["technique"]
                            )
                            changed_own_technique.left_position = Position.objects.get(
                                profile=profile, side=True, number=own_technique["left"]
                            )
                            changed_own_technique.right_position = Position.objects.get(
                                profile=profile,
                                side=False,
                                number=own_technique["right"],
                            )
                            changed_own_technique.save()
                    # delete own technique if profile matches
                    case "delete":
                        to_be_deleted = OwnTechnique.objects.get(id=own_technique["id"])
                        if to_be_deleted.profile == profile:
                            to_be_deleted.delete()

            # ranks
            for rank_item in data["rank_items"]:
                match rank_item["action"]:
                    # create new rank item
                    case "add":
                        if rank_item["type"] == "combination":
                            new_rank_item = CombinationRank(
                                number=rank_item["number"],
                                technique1=Technique.objects.get(
                                    id=rank_item["technique1"]
                                ),
                                technique2=Technique.objects.get(
                                    id=rank_item["technique2"]
                                ),
                                profile=profile,
                            )
                        else:
                            new_rank_item = TechniqueRank(
                                number=rank_item["number"],
                                technique=Technique.objects.get(
                                    id=rank_item["technique"]
                                ),
                                profile=profile,
                                type=int(rank_item["type"] == "special"),
                            )
                        new_rank_item.save()
                    # update rank item if profile matches
                    case "update":
                        if rank_item["type"] == "combination":
                            changed_rank_item = CombinationRank.objects.get(
                                id=rank_item["id"]
                            )
                            changed_rank_item.number = rank_item["number"]
                            changed_rank_item.technique1 = Technique.objects.get(
                                id=rank_item["technique1"]
                            )
                            changed_rank_item.technique2 = Technique.objects.get(
                                id=rank_item["technique2"]
                            )
                        else:
                            changed_rank_item = TechniqueRank.objects.get(
                                id=rank_item["id"]
                            )
                            changed_rank_item.number = rank_item["number"]
                            changed_rank_item.technique = Technique.objects.get(
                                id=rank_item["technique"]
                            )
                            changed_rank_item.type = rank_item["type"]
                        if changed_rank_item.profile == profile:
                            changed_rank_item.save()
                    # delete rank item if profile matches
                    case "delete":
                        if rank_item["type"] == "combination":
                            to_be_deleted = CombinationRank.objects.get(
                                id=rank_item["id"]
                            )
                        else:
                            to_be_deleted = TechniqueRank.objects.get(
                                id=rank_item["id"]
                            )
                        if to_be_deleted.profile == profile:
                            to_be_deleted.delete()

            if data["action"] == "save":
                # reload page if "save" button was pressed
                return redirect("profiles-profile-edit", username=profile.user.username)
            else:
                # otherwise redirect to edited profile
                return redirect("profiles-profile", username=profile.user.username)

    else:
        # collect relevant data
        profile = User.objects.get(username=username).profile
        own_techniques = OwnTechnique.objects.filter(profile=profile)
        stechniques = Technique.objects.filter(type="S").order_by("name")
        gtechniques = Technique.objects.filter(type="B").order_by("name")
        techniques = Technique.objects.all().order_by("name")
        positions = Position.objects.filter(profile=profile)
        technique_ranks = TechniqueRank.objects.filter(profile=profile).order_by(
            "number"
        )
        combination_rank = CombinationRank.objects.filter(profile=profile).order_by(
            "number"
        )

        # return template with profile data and techniques
        return render(
            request,
            "profiles/edit.html",
            {
                "profile": profile,
                "own_techniques": own_techniques,
                "stechniques": stechniques,
                "gtechniques": gtechniques,
                "techniques": techniques,
                "positions": positions,
                "technique_ranks": technique_ranks,
                "combination_rank": combination_rank,
            },
        )


@object_permission_required(
    "profiles.change_profile", (Profile, "user__username", "username")
)
def manage_profile(request, username):
    profile = User.objects.get(username=username).profile
    # get all users where profile permission is allowed to be changed
    users = User.objects.exclude(
        Q(is_superuser=True)
        | Q(id__in=[request.user.id, profile.created_by.id, profile.user.id])
        | Q(is_active=False)
    ).order_by("username")

    if request.method == "POST":
        # change permissions
        if "update" in request.POST:
            permission = request.POST["permission"]
            permissions = ["view_profile", "change_profile", "manage_profile"]
            # variable for users who shouldn't have the permission
            remove = users
            for id in request.POST:
                # try only if element is an integer
                if id.isdigit():
                    try:
                        user = User.objects.get(id=int(id))
                        # check if user can have the permission
                        if (
                            permission == "view_profile"
                            or user.groups.filter(name="Trainers").exists()
                        ):
                            # assign the permission and all of lower privilege
                            for p in permissions[: permissions.index(permission) + 1]:
                                assign_perm(p, user, profile)
                            # remove user from remove list
                            remove = remove.exclude(id=int(id))
                    except (User.DoesNotExist, ValueError):
                        pass

            # remove the permission and all of higher privilege from left users
            for user in remove:
                for p in permissions[permissions.index(permission) :]:
                    remove_perm(p, user, profile)

            # return success for htmx
            return HttpResponse(_("Saved"))

        # htmx user search
        elif "search" in request.POST:
            search = request.POST["search"]
            permission = request.POST["permission"]
            # remove non trainers if permission is higher than view
            if permission != "view_profile":
                users = users.filter(groups__name="Trainers")
            filtered = users.filter(
                Q(first_name__icontains=search) | Q(last_name__icontains=search)
            )

            # return html table for htmx
            return render(
                request,
                "htmx/profile_permissions.html",
                {"users": filtered, "profile": profile, "permission": permission},
            )
        # if the profiles user is not active manage token
        elif not profile.user.is_active:
            if "add" in request.POST:
                Token(user=profile.user).save()
            elif "renew" in request.POST:
                user = profile.user
                user.token.delete()
                Token(user=user).save()
            elif "delete_token" in request.POST:
                profile.user.token.delete()

            # reload the page
            return redirect("profiles-profile-manage", username=username)
    else:
        # get plural translation
        try:
            count = profile.user.token.valid_for
            days = ngettext(
                "Valid for %(count)d day", "Valid for %(count)d days", count
            ) % {"count": count}
        except Token.DoesNotExist:
            days = None

        # return template with profile data
        return render(
            request, "profiles/manage.html", {"profile": profile, "days": days}
        )
