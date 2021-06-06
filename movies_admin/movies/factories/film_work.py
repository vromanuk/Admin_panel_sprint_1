import datetime
import random
import uuid

import factory

from ..models import FilmWork, MovieType


class FilmWorkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FilmWork
        django_get_or_create = ("uuid",)

    title = factory.Sequence(lambda n: "Movie Title%s" % n)
    description = factory.Sequence(lambda n: "Movie Description%s" % n)
    creation_date = factory.LazyFunction(datetime.datetime.now)
    certificate = factory.Sequence(lambda n: "Movie Certificate%s" % n)
    rating = random.randint(0, 9)
    type = MovieType.MOVIE
    uuid = uuid.uuid4()

    @factory.post_generation
    def genres(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of genres were passed in, use them
            for genre in extracted:
                self.genres.add(genre)

    @factory.post_generation
    def people(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of genres were passed in, use them
            for person in extracted:
                self.people.add(person)
