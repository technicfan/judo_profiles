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

import binascii
import hashlib
import hmac
import os

from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.contrib.sessions.models import Session

from .models import Profile, Token


# check if user is staff
def is_staff(user):
    return user.is_staff


# check if user is admin
def is_admin(user):
    return user.is_superuser


def new_token(user):
    if not Token.objects.filter(user=user).exists():
        token = binascii.hexlify(os.urandom(8), "-", 2).decode().upper()
        Token(
            token=hmac.new(
                settings.SECRET_KEY.encode(), token.encode(), hashlib.sha256
            ).hexdigest(),
            user=user,
        ).save()

        return token
    else:
        return None


# create unique username for new user
def unique_username(username: str) -> str:
    # check how often initial name already exists
    number = User.objects.filter(username__regex=rf"^{username}([0-9]*)?$").count()
    # return unique username
    if number != 0:
        return f"{username}{number}"
    else:
        return username


# delete all sessions for user
def logout_all(user):
    for s in Session.objects.all():
        if s.get_decoded().get("_auth_user_id") == str(user.id):
            s.delete()


# add user to trainers group
def toggle_trainer(user):
    group, created = Group.objects.get_or_create(name="Trainers")
    if created:
        permission = Permission.objects.get(codename="add_profile")
        group.permissions.add(permission)
    if user.groups.filter(name="Trainers").exists():
        user.groups.remove(group)
    else:
        user.groups.add(group)


def token_actions(request, user, staff=False):
    if "add" in request:
        return new_token(user)
    elif "renew" in request:
        try:
            Token.objects.get(user=user).delete()
        except Token.DoesNotExist:
            pass
        return new_token(user)
    elif "delete" in request:
        try:
            Token.objects.get(user=user).delete()
        except Token.DoesNotExist:
            pass
        return None
    elif "reset" in request and staff:
        try:
            Token.objects.get(user=user).delete()
        except Token.DoesNotExist:
            pass
        # logout everywhere after creation of token to reset password
        logout_all(user)
        return new_token(user)


def user_actions(request, user, superuser=False):
    if "delete" in request and superuser:
        for i in Profile.objects.filter(creator=user):
            i.creator = i.manager
            i.save()
        for i in Profile.objects.filter(manager=user):
            i.manager = i.creator
            i.save()
        user.delete()
    elif "deactivate" in request:
        try:
            user.set_unusable_password()
            user.is_active = False
            user.save()
            Token.objects.get(user=user).delete()
        except Token.DoesNotExist:
            pass
        logout_all(user)
    elif "trainer" in request:
        toggle_trainer(user)
    elif "staff" in request and superuser:
        user.is_staff = not user.is_staff
        user.save()
