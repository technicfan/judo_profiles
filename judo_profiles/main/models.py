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
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, related_name="fighter")
    can_be_seen_by = models.ManyToManyField(User, blank=True, related_name="fighters_visible")
    weight = models.FloatField()
    primary_side = models.PositiveIntegerField(choices=PRIMARY_SIDE_CHOICES)
    year = models.PositiveIntegerField()
    nationality = models.CharField(max_length=10)
    positive_comments = models.TextField(null=True, blank=True)
    negative_comments = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fighters_created")
    updated_on = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.last_name}, {self.name}"

class Position(models.Model):
    SIDE_CHOICES = [
        (True, "Left"),
        (False, "Right")
    ]
    fighter_profile = models.ForeignKey(Fighter, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    side = models.BooleanField(choices=SIDE_CHOICES)
    x = models.IntegerField()
    y = models.IntegerField()

class Technique(models.Model):
    codename = models.CharField(max_length=3)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=1)

    def __str__(self):
        return self.name

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

    def __str__(self):
        return self.technique.name

class SpecialTechnique(models.Model):
    fighter_profile = models.ForeignKey(Fighter, on_delete=models.CASCADE)
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()

    def __str__(self):
        return self.technique.name

class Combination(models.Model):
    fighter_profile = models.ForeignKey(Fighter, on_delete=models.CASCADE)
    technique1 = models.ForeignKey(Technique, on_delete=models.CASCADE, related_name="technique1_combinations")
    technique2 = models.ForeignKey(Technique, on_delete=models.CASCADE, related_name="technique2_combinations")
    number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.technique1.name}, {self.technique2.name}"
    
