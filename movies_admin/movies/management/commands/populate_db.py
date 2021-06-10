import random
import uuid

from django.core.management import BaseCommand
from django.db import transaction
from movies.factories.film_work import CastFactory, FilmWorkFactory
from movies.factories.genre import GenreFactory
from movies.factories.person import PersonFactory, RoleFactory

GENRES_TOTAL = 10
ROLES_TOTAL = 10


class Command(BaseCommand):
    help = "Populates db"

    def add_arguments(self, parser):
        parser.add_argument("total", type=int, help="Indicates the number of film_works/people to be created")

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Populating DB")
        total = kwargs["total"]
        genres = GenreFactory.create_batch(size=GENRES_TOTAL)
        roles = RoleFactory.create_batch(size=ROLES_TOTAL)
        for _ in range(total):
            film_work_genres = random.choices(genres, k=4)
            film_work = FilmWorkFactory.build(uuid=uuid.uuid4())
            person = PersonFactory.build(uuid=uuid.uuid4())
            film_work.save()
            [film_work.genres.add(genre) for genre in film_work_genres]
            person.save()
            role = random.choices(roles)[0]
            CastFactory.create(person=person, film_work=film_work, role=role)
        self.stdout.write("Success. DB has been populated!")
