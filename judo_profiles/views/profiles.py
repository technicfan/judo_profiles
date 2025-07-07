# Copyright (C) 2025 technicfan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from django.views.decorators.http import require_http_methods
from guardian.decorators import permission_required as object_permission_required
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm

from ..models import (
    CombinationRank,
    OwnTechnique,
    Position,
    Profile,
    Technique,
    TechniqueRank,
)
from ..utils import token_actions, unique_username


# list all available profiles
@require_http_methods(["GET", "POST"])
def profiles(request):
    if request.method == "POST":
        # get profiles with search
        shown_profiles = get_objects_for_user(
            request.user, "judo_profiles.view_profile"
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


@require_http_methods(["GET", "POST"])
@permission_required("judo_profiles.add_profile")
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
            creator=request.user,
            manager=request.user,
        )
        try:
            if data["user"] is not None:
                newuser = User.objects.get(id=data["user"])
            else:
                raise User.DoesNotExist
        except User.DoesNotExist:
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
        assign_perm("manage_profile", newuser, profile)
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
                    type=int(rank_item["type"] == "special"),
                )
            new_rank_item.save()

        # redirect to created profile
        return redirect("profile", username=profile.user.username)
    else:
        stechniques = Technique.objects.filter(type="S").order_by("name")
        gtechniques = Technique.objects.filter(type="B").order_by("name")
        techniques = Technique.objects.all().order_by("name")
        users = User.objects.exclude(is_superuser=True).exclude(id=request.user.id)
        for user in users:
            if Profile.objects.filter(user=user).exists():
                users = users.exclude(username=user.username)

        # return template with techniques
        return render(
            request,
            "profiles/new.html",
            {
                "techniques": techniques,
                "stechniques": stechniques,
                "gtechniques": gtechniques,
                "users": users,
            },
        )


@require_http_methods(["GET"])
@object_permission_required(
    "judo_profiles.view_profile", (Profile, "user__username", "username")
)
def profile(request, username):
    # collect profile data
    profile = Profile.objects.get(user__username=username)
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


@require_http_methods(["GET", "POST"])
@object_permission_required(
    "judo_profiles.change_profile", (Profile, "user__username", "username")
)
def edit_profile(request, username):
    if request.method == "POST":
        data = json.loads(request.body)

        profile = Profile.objects.get(user__username=username)

        if data["action"] == "delete" and (
            request.user == profile.manager or request.user.is_superuser
        ):
            # delete profile and inactive user
            if profile.user.is_active:
                profile.delete()
            else:
                profile.user.delete()

            return redirect("profiles")
        elif data["changed"]:
            # profile
            profile.name = data["name"]
            profile.last_name = data["last_name"]
            profile.year = data["year"]
            profile.weight = data["weight"]
            profile.primary_side = data["side"]
            profile.changed_by = request.user
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
            return redirect("edit-profile", username=profile.user.username)
        else:
            # otherwise redirect to edited profile
            return redirect("profile", username=profile.user.username)

    else:
        # collect relevant data
        profile = Profile.objects.get(user__username=username)
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


@require_http_methods(["GET", "POST"])
@object_permission_required(
    "judo_profiles.manage_profile", (Profile, "user__username", "username")
)
def manage_profile(request, username):
    profile = Profile.objects.get(user__username=username)
    # get all users where profile permission is allowed to be changed
    users = User.objects.exclude(
        Q(is_superuser=True)
        | Q(id__in=[request.user.id, profile.manager.id, profile.user.id])
        | Q(is_active=False)
    ).order_by("username")

    if request.method == "POST":
        # change permissions
        if "update" in request.POST:
            permission = request.POST["permission"]
            permissions = ["view_profile", "change_profile"]
            if permission in permissions:
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
                                assign_perm(permission, user, profile)
                                if permission != "view_profile":
                                    assign_perm("view_profile", user, profile)
                                # remove user from remove list
                                remove = remove.exclude(id=int(id))
                        except (User.DoesNotExist, ValueError):
                            pass

                # remove the permission and all of higher privilege from left users
                for user in remove:
                    if permission == "view_profile":
                        for p in permissions:
                            remove_perm(p, user, profile)
                    else:
                        remove_perm(permission, user, profile)

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
        elif "manager" in request.POST and profile.manager == request.user:
            try:
                new_manager = User.objects.get(username=request.POST["manager"])
                if (
                    new_manager.is_superuser
                    or new_manager.groups.filter(name="Trainers").exists()
                ):
                    profile.manager = new_manager
                    profile.save()
                    if not request.user == profile.creator:
                        remove_perm("view_profile", request.user, profile)
                    remove_perm("change_profile", request.user, profile)
                    remove_perm("manage_profile", request.user, profile)
                    assign_perm("view_profile", new_manager, profile)
                    assign_perm("change_profile", new_manager, profile)
                    assign_perm("manage_profile", new_manager, profile)
                else:
                    raise User.DoesNotExist
                return redirect("profiles")
            except User.DoesNotExist:
                pass
        # if the profiles user is not active manage token
        elif not profile.user.is_active:
            result = token_actions(request.POST, profile.user)
            if result is not None:
                return render(request, "htmx/token.html", {"token": result})

        # reload the page
        return redirect("manage-profile", username=username)
    else:
        # get plural translation
        days = ngettext("Valid for %(count)d day", "Valid for %(count)d days", 2) % {
            "count": 2
        }

        # return template with profile data
        return render(
            request,
            "profiles/manage.html",
            {
                "profile": profile,
                "days": days,
                "trainers": User.objects.filter(
                    Q(groups__name="Trainers") | Q(is_superuser=True)
                ).exclude(Q(id=request.user.id) | Q(id=profile.user.id)),
            },
        )
