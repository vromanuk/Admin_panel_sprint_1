import uuid

import factory.fuzzy
from movies.models import Person, Role


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Person
        django_get_or_create = ("uuid",)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    uuid = uuid.uuid4()


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role

    role = factory.fuzzy.FuzzyChoice(Role.RoleType.choices, getter=lambda c: c[0])
