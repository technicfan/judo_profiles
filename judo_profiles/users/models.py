from django.contrib.auth.models import User
from django.db import models
from datetime import date
import uuid


def gen_token() -> str:
    return uuid.uuid4().hex


class Token(models.Model):
    token = models.CharField(default=gen_token, max_length=32, blank=True, editable=False, unique=True)
    created = models.DateField(auto_now_add=True)
    trainer = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    valid_days = models.PositiveIntegerField(default=14)

    def __str__(self):
        return self.token

    @property
    def expired(self):
        return (date.today() - self.created).days > self.valid_days
