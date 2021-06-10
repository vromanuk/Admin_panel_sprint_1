import uuid

import factory.fuzzy
from movies.models import Person, Role


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Person
        django_get_or_create = ("uuid",)

    first_name = factory.Sequence(lambda n: "user {:02}".format(n))
    last_name = factory.Sequence(lambda n: "last {:02}".format(n))
    uuid = uuid.uuid4()


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role
        django_get_or_create = ("role",)

    role = factory.fuzzy.FuzzyChoice(Role.RoleType.choices, getter=lambda c: c[0])
