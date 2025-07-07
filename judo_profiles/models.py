import hashlib
import hmac
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _


class Server(models.Model):
    imprint = models.TextField(blank=True, null=True)
    privacy_contact = models.TextField(blank=True, null=True)
    changed = models.BooleanField(default=False)


class Token(models.Model):
    token = models.CharField(editable=False, unique=True)
    created_at = models.DateField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.token

    @property
    def valid_for(self):
        return (self.created_at + timedelta(days=2) - date.today()).days

    @property
    def valid(self):
        return self.valid_for > 0

    def validate(self, token):
        return (
            self.valid
            and self.token
            == hmac.new(
                settings.SECRET_KEY.encode(), token.upper().encode(), hashlib.sha256
            ).hexdigest()
        )


class Profile(models.Model):
    PRIMARY_SIDE_CHOICES = [(1, "Left"), (2, "Right"), (3, "Both")]
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    weight = models.FloatField()
    primary_side = models.PositiveIntegerField(choices=PRIMARY_SIDE_CHOICES)
    year = models.PositiveIntegerField()
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="profiles_created"
    )
    manager = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="profiles_managed"
    )
    created_at = models.DateField(auto_now_add=True)
    changed_at = models.DateField(auto_now=True)
    changed_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="profiles_changed",
    )

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
