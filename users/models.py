from django.contrib.auth.models import User
from django.db import models
from datetime import date, timedelta
import uuid


def gen_token() -> str:
    return uuid.uuid4().hex


def calc_date():
    return date.today() + timedelta(days=7)


class Token(models.Model):
    token = models.CharField(
        default=gen_token,
        max_length=32,
        blank=True,
        editable=False,
        unique=True
    )
    valid_until = models.DateField(default=calc_date)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.token

    @property
    def valid_for(self):
        return (self.valid_until - date.today()).days
