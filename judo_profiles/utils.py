from django.contrib.auth.models import Group, Permission, User
from django.contrib.sessions.models import Session

from .models import Token


# check if user is staff
def is_staff(user):
    return user.is_superuser or user.is_staff


# check if user is admin
def is_admin(user):
    return user.is_superuser


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
        Token(user=user).save()
    elif "renew" in request:
        try:
            Token.objects.get(user=user).delete()
        except Token.DoesNotExist:
            pass
        Token(user=user).save()
    elif "delete" in request:
        try:
            Token.objects.get(user=user).delete()
        except Token.DoesNotExist:
            pass
    elif "reset" in request and staff:
        try:
            Token.objects.get(user=user).delete()
        except Token.DoesNotExist:
            pass
        Token(user=user).save()
        # logout everywhere after creation of token to reset password
        logout_all(user)


def user_actions(request, user, superuser=False):
    if "delete" in request and superuser:
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
