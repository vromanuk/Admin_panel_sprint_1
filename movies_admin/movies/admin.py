from django.contrib import admin

from .models import FilmWork


@admin.register(FilmWork)
class MovieAdmin(admin.ModelAdmin):
    # отображение полей в списке
    list_display = ("title", "type", "creation_date", "rating", "created", "modified")

    # фильтрация в списке
    list_filter = ("type",)

    # поиск по полям
    search_fields = ("title", "description", "id")

    # порядок следования полей в форме создания/редактирования
    fields = (
        "title",
        "type",
        "description",
        "creation_date",
        "certificate",
        "file_path",
        "rating",
    )
