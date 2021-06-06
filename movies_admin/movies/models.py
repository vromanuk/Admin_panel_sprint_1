import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Person(TimeStampedModel):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    role = models.CharField(_("роль"), max_length=45)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        verbose_name = _("актеры, режиссеры и сценаристы")
        verbose_name_plural = _("состав")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Genre(TimeStampedModel):
    genre = models.CharField(_("название"), max_length=45, unique=True)

    class Meta:
        verbose_name = _("жанр")
        verbose_name_plural = _("жанры")

    def __str__(self):
        return self.genre


class MovieType(models.TextChoices):
    MOVIE = "movie", _("фильм")
    TV_SHOW = "tv_show", _("шоу")


class FilmWork(TimeStampedModel):
    title = models.CharField(_("название"), max_length=255)
    description = models.TextField(_("описание"), blank=True)
    creation_date = models.DateField(_("дата создания фильма"), blank=True)
    certificate = models.TextField(_("сертификат"), blank=True)
    file_path = models.FileField(_("файл"), upload_to="film_works/", blank=True, null=True)
    rating = models.FloatField(_("рейтинг"), validators=[MinValueValidator(0)], blank=True)
    type = models.CharField(_("тип"), max_length=20, choices=MovieType.choices)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    genres = models.ManyToManyField(Genre)
    people = models.ManyToManyField(Person)

    class Meta:
        verbose_name = _("кинопроизведение")
        verbose_name_plural = _("кинопроизведения")

    def __str__(self):
        return self.title
