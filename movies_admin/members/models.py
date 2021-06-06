from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class User(TimeStampedModel, AbstractUser):
    email = models.EmailField(_("email address"), max_length=255, unique=True, db_index=True)
    password = models.CharField(_("password"), max_length=255, blank=True)

    objects = UserManager()


class Membership(models.Model):
    class Roles(models.IntegerChoices):
        MOVIES_VIEW = 1
        MOVIES_ADMIN = 2
        SECURITY_OFFICER = 3

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="membership")
    role = models.IntegerField(choices=Roles.choices, default=Roles.MOVIES_VIEW)
