import binascii
import os
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _


def gen_token() -> str:
    return binascii.hexlify(os.urandom(20)).decode()


def calc_date():
    return date.today() + timedelta(days=7)


class Token(models.Model):
    token = models.CharField(
        default=gen_token, max_length=40, editable=False, unique=True
    )
    valid_until = models.DateField(default=calc_date)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.token

    @property
    def valid_for(self):
        return (self.valid_until - date.today()).days


class Profile(models.Model):
    PRIMARY_SIDE_CHOICES = [(1, "Left"), (2, "Right"), (3, "Both")]
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    weight = models.FloatField()
    primary_side = models.PositiveIntegerField(choices=PRIMARY_SIDE_CHOICES)
    year = models.PositiveIntegerField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="profiles_created"
    )
    updated_on = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.last_name}, {self.name}"

    class Meta:
        permissions = (("manage_profile", "Manage Permissions"),)


class Position(models.Model):
    SIDE_CHOICES = [(True, "l"), (False, "r")]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    side = models.BooleanField(choices=SIDE_CHOICES)
    x = models.FloatField()
    y = models.FloatField()


class Technique(models.Model):
    codename = models.CharField(max_length=3)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=1)

    def __str__(self):
        return self.name


class OwnTechnique(models.Model):
    SIDE_CHOICES = [(True, "l"), (False, "r")]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE)
    side = models.BooleanField(choices=SIDE_CHOICES)
    state = models.PositiveIntegerField()
    direction = models.PositiveIntegerField()
    left_position = models.ForeignKey(
        Position, on_delete=models.CASCADE, related_name="left_position_owntechniques"
    )
    right_position = models.ForeignKey(
        Position, on_delete=models.CASCADE, related_name="right_position_owntechniques"
    )

    def __str__(self):
        return self.technique.name

    @property
    def state_local(self):
        match self.state:
            case 0:
                return _("Stable_short")
            case 1:
                return _("Training_short")
            case 2:
                return _("Learn_short")


class TechniqueRank(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    type = models.PositiveIntegerField()

    def __str__(self):
        return self.technique.name


class CombinationRank(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    technique1 = models.ForeignKey(
        Technique, on_delete=models.CASCADE, related_name="technique1_combinations"
    )
    technique2 = models.ForeignKey(
        Technique, on_delete=models.CASCADE, related_name="technique2_combinations"
    )
    number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.technique1.name}, {self.technique2.name}"
