import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Person(TimeStampedModel):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = _("актеры, режиссеры и сценаристы")
        verbose_name_plural = _("состав")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Role(TimeStampedModel):
    class RoleType(models.TextChoices):
        ACTOR = "actor", _("актёр")
        DIRECTOR = "director", _("режиссёр")
        WRITER = "writer", _("сценарист")

    role = models.CharField(_("тип"), max_length=45, choices=RoleType.choices, unique=True)

    def __str__(self):
        return self.role


class Genre(TimeStampedModel):
    genre = models.CharField(_("название"), max_length=45, unique=True)

    class Meta:
        verbose_name = _("жанр")
        verbose_name_plural = _("жанры")

    def __str__(self):
        return self.genre


class FilmWork(TimeStampedModel):
    class MovieType(models.TextChoices):
        MOVIE = "movie", _("фильм")
        TV_SHOW = "tv_show", _("шоу")

    title = models.CharField(_("название"), max_length=255)
    description = models.TextField(_("описание"), blank=True)
    creation_date = models.DateField(_("дата создания фильма"), blank=True)
    certificate = models.TextField(_("сертификат"), blank=True)
    file_path = models.FileField(_("файл"), upload_to="film_works/", blank=True, null=True)
    rating = models.FloatField(_("рейтинг"), validators=[MinValueValidator(0)], blank=True)
    type = models.CharField(_("тип"), max_length=20, choices=MovieType.choices)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    genres = models.ManyToManyField(Genre, related_name="film_works")
    people = models.ManyToManyField(Person, related_name="film_works", through="Cast")

    class Meta:
        verbose_name = _("кинопроизведение")
        verbose_name_plural = _("кинопроизведения")

    def __str__(self):
        return self.title


class Cast(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("person", "film_work")
