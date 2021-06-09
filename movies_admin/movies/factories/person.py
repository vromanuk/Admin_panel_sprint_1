import random
import uuid

import factory
from django.utils.translation import gettext_lazy as _
from movies.models import Person

roles = [_("актёр"), _("сценарист"), _("режиссёр")]


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Person
        django_get_or_create = ("uuid",)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = random.choice(roles)
    uuid = uuid.uuid4()
