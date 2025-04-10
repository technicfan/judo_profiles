from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    PRIMARY_SIDE_CHOICES = [
        (1, "Left"),
        (2, "Right"),
        (3, "Both")
    ]
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    weight = models.FloatField()
    primary_side = models.PositiveIntegerField(choices=PRIMARY_SIDE_CHOICES)
    year = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profiles_created")
    updated_on = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.last_name}, {self.name}"

    class Meta:
        permissions = (
            ("manage_profile", "Manage Permissions"),
        )


class Position(models.Model):
    SIDE_CHOICES = [
        (True, "l"),
        (False, "r")
    ]
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
    SIDE_CHOICES = [
        (True, "l"),
        (False, "r")
    ]
    STATE_CHOICES = [
        ("W", "wettkampfstabil"),
        ("T", "Training"),
        ("Z", "zu lernen"),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE)
    side = models.BooleanField(choices=SIDE_CHOICES)
    state = models.CharField(max_length=1, choices=STATE_CHOICES)
    direction = models.PositiveIntegerField()
    left_position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name="left_position_owntechniques"
    )
    right_position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name="right_position_owntechniques"
    )

    def __str__(self):
        return self.technique.name


class TechniqueRank(models.Model):
    TYPE_CHOICES = [
        ("S", "Spezial"),
        ("U", "Übergang"),
        ("B", "Boden")
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    type = models.CharField(choices=TYPE_CHOICES, max_length=1)

    def __str__(self):
        return self.technique.name


class CombinationRank(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    technique1 = models.ForeignKey(
        Technique,
        on_delete=models.CASCADE,
        related_name="technique1_combinations"
    )
    technique2 = models.ForeignKey(
        Technique,
        on_delete=models.CASCADE,
        related_name="technique2_combinations"
    )
    number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.technique1.name}, {self.technique2.name}"
