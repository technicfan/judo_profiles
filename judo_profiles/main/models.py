from django.db import models
from django.contrib.auth.models import User

class Fighter(models.Model):
    PRIMARY_SIDE_CHOICES = [
        (1, "Left"),
        (2, "Right"),
        (3, "Both")
    ]
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, related_name='fighter')
    can_be_seen_by = models.ManyToManyField(User, blank=True, related_name='fighters_visible')
    weight = models.FloatField()
    primary_side = models.IntegerField(choices=PRIMARY_SIDE_CHOICES)
    year = models.IntegerField()
    nationality = models.CharField(max_length=10)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fighters_created')
    updated_on = models.DateField(auto_now=True)

    def __str__(self):
        return self.last_name + ", " + self.name

class Position(models.Model):
    fighter_profile = models.ForeignKey(Fighter, on_delete=models.CASCADE)
    side = models.BooleanField()
    x = models.IntegerField()
    y = models.IntegerField()

class Technique(models.Model):
    codename = models.CharField(max_length=3)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=1)

class OwnTechnique(models.Model):
    SIDE_CHOICES = [
        (True, "Left"),
        (False, "Right")
    ]
    fighter_profile = models.ForeignKey(Fighter, on_delete=models.CASCADE)
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE)
    side = models.BooleanField(choices=SIDE_CHOICES)
    state = models.CharField(max_length=1)
    positions = models.ManyToManyField(Position)
