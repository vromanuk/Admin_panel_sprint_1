from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _

from .models import FilmWork, Genre, Person


@admin.register(FilmWork)
class MovieAdmin(admin.ModelAdmin):
    filter_horizonal = ("people", "genres")
    list_display = ("title", "type", "creation_date", "rating", "created", "modified")
    list_filter = ("created", "title")
    search_fields = ("title", "description", "id")

    fields = (
        "title",
        "type",
        "description",
        "creation_date",
        "certificate",
        "file_path",
        "rating",
        "genres",
        "people",
    )


class PersonAdminForm(forms.ModelForm):
    film_works = forms.ModelMultipleChoiceField(
        queryset=FilmWork.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name=_("кинопроизведения"), is_stacked=False),
    )

    class Meta:
        model = Person
        exclude = ["id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["film_works"].initial = self.instance.film_works.all()

    def save(self, commit=True):
        person = super().save(commit=False)

        if commit:
            person.save()

        if person.pk:
            person.film_works.set(self.cleaned_data["film_works"])
            self.save_m2m()

        return person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    form = PersonAdminForm

    search_fields = ("first_name", "last_name")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("genre", "id")
    list_filter = ("genre",)
    search_fields = ("genre",)
