import random

import factory
from django.utils.translation import gettext_lazy as _
from movies.models import Genre

genres = [_("Action"), _("Adventure"), _("Fantasy"), _("Sci-Fi"), _("Drama"), _("Music"), _("Thriller"), _("Comedy")]


class GenreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Genre
        django_get_or_create = ("genre",)

    genre = random.choice(genres)
