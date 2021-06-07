import json
import sqlite3
import uuid
from dataclasses import astuple, dataclass
from typing import List

from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_batch


@dataclass
class Movie:
    id: str
    title: str
    imdb_rating: float
    description: str
    type: str = "movie"


@dataclass
class Person:
    id: str
    name: str


@dataclass
class MoviePeople:
    id: str
    movie_id: str
    person_id: str


@dataclass
class Genre:
    id: str
    genre: str


@dataclass
class MovieGenres:
    id: str
    movie_id: str
    genre: str


class PostgresSaver:
    def __init__(self, conn: _connection):
        self.conn = conn

    def save_all_data(self, records: List[dict]):
        genres = []
        movie_people = []
        movie_genres = []

        for record in records:
            genres.append(record["genres"])
            movie_people.append(record["movie_people"])
            movie_genres.append(record["movie_genres"])

        with self.conn.cursor() as cur:
            print("insert movies")
            execute_batch(
                cur,
                """
                    INSERT INTO content.film_work (id, title, rating, description, type, created_at)
                    VALUES (%s, %s, %s, %s, %s, now())
                """,
                [astuple(record["movie"]) for record in records],
                page_size=5_000,
            )
            self.conn.commit()
            print("movies has been inserted")

            people, movie_people = self.unify_people(movie_people)
            print("insert people")
            execute_batch(
                cur,
                "INSERT INTO content.person (id, name) VALUES (%s, %s)",
                [astuple(person) for person in people],
                page_size=5_000,
            )
            self.conn.commit()
            print("people has been inserted")

            print("insert movie_people")
            execute_batch(
                cur,
                "INSERT INTO content.person_film_work (id, film_work_id, person_id) VALUES (%s, %s, %s)",
                [astuple(movie_person) for movie_person in movie_people],
                page_size=5_000,
            )
            self.conn.commit()
            print("movie_people has been inserted")

            genres, movie_genres = self.unify_genres(genres, movie_genres)
            print("insert genres")
            execute_batch(
                cur,
                "INSERT INTO content.genre (id, genre) VALUES (%s, %s)",
                [astuple(genre) for genre in genres],
                page_size=5_000,
            )
            self.conn.commit()
            print("genres has been inserted")

            print("insert movie_genres")
            execute_batch(
                cur,
                "INSERT INTO content.genre_film_work (id, film_work_id, genre) VALUES (%s, %s, %s)",
                [astuple(movie_genre) for movie_genre in movie_genres],
                page_size=5_000,
            )
            self.conn.commit()
            print("movie_genres has been inserted")

    @staticmethod
    def unify_genres(genres: list[list[Genre]], movie_genres: list[dict]) -> tuple[list[Genre], list[MovieGenres]]:
        existent_genres = set()
        unified_genres = []
        unified_movie_genres = []
        for duplicate_genres in genres:
            for genre in duplicate_genres:
                current_genre = genre.genre
                if current_genre in existent_genres:
                    continue
                unified_genres.append(genre)
                existent_genres.add(current_genre)

        for data in movie_genres:
            movie_id = data["movie_id"]
            for movie_genre in data["genres"]:
                unified_movie_genres.append(
                    MovieGenres(id=str(uuid.uuid4()), movie_id=movie_id, genre=movie_genre.genre)
                )
        return unified_genres, unified_movie_genres

    @staticmethod
    def unify_people(movie_people: list[dict]) -> tuple:
        existent_people = {}
        unified_people = []
        unified_movie_people = []

        for data in movie_people:
            for person in data["people"]:
                name = person.name
                if name in existent_people:
                    continue
                unified_movie_people.append(
                    MoviePeople(id=str(uuid.uuid4()), movie_id=data["movie_id"], person_id=person.id)
                )
                unified_people.append(person)
                existent_people[name] = person.id

        return unified_people, unified_movie_people


class SQLiteLoader:
    SQL = """
    /* Используем CTE для читаемости. Здесь нет прироста
    производительности, поэтому можно поменять на subquery */
    WITH x as (
        -- Используем group_concat, чтобы собрать id и имена
        -- всех актёров в один список после join'а с таблицей actors
        -- Отметим, что порядок id и имён совпадает
        -- Не стоит забывать про many-to-many связь между
        -- таблицами фильмов и актёров
        SELECT m.id, group_concat(a.id) as actors_ids, group_concat(a.name) as actors_names
        FROM movies m
                 LEFT JOIN movie_actors ma on m.id = ma.movie_id
                 LEFT JOIN actors a on ma.actor_id = a.id
        GROUP BY m.id
    )
    -- Получаем список всех фильмов со сценаристами и актёрами
    SELECT m.id, genre, director, title, plot, imdb_rating, x.actors_ids, x.actors_names,
         /* Этот CASE решает проблему в дизайне таблицы:
        если сценарист всего один, то он записан простой строкой
        в столбце writer и id. В противном случае данные
        хранятся в столбце writers  и записаны в виде
        списка объектов JSON.
        Для исправления ситуации применяем хак:
        приводим одиночные записи сценаристов к списку
        из одного объекта JSON и кладём всё в поле writers */
           CASE
            WHEN m.writers = '' THEN '[{"id": "' || m.writer || '"}]'
            ELSE m.writers
           END AS writers
    FROM movies m
    LEFT JOIN x ON m.id = x.id
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def load_writers_names(self) -> dict:
        """
        Получаем список всех сценаристов, так как нет возможности
        получить их в одном запросе
        :return: словарь всех сценаристов вида
        {
            "Writer": {"id": "writer_id", "name": "Writer"},
            ...
        }
        """
        writers = {}
        # Используем DISTINCT, чтобы отсекать возможные дубли
        for writer in self.conn.execute("""SELECT id, name FROM writers"""):
            w = Person(id=str(uuid.uuid4()), name=writer[1])
            writers[writer[0]] = w
        return writers

    @staticmethod
    def _transform_row(row: tuple, writers: dict) -> dict:
        """
         Основная логика преобразования данных из SQLite во внутреннее
             представление, которое дальше будет уходить в Elasticsearch
        Решаемы проблемы:
         1) genre в БД указан в виде строки из одного или нескольких
         жанров, разделённых запятыми -> преобразовываем в список жанров.
         2) writers из запроса в БД приходит в виде списка словарей id'шников
         -> обогащаем именами из полученных заранее сценаристов
         и добавляем к каждому id ещё и имя
         3) actors формируем из двух полей запроса (actors_ids и actors_names)
         в список словарей, наподобие списка сценаристов.
         4) для полей writers, imdb_rating, director и description меняем
         поля 'N/A' на None.

         :param row: строка из БД
         :param writers: текущие сценаристы
         :return: подходящая строка для сохранения в Elasticsearch
        """

        people = []
        movie_writers = []
        writers_set = set()
        for writer in json.loads(row[-1]):
            writer_id = writer["id"]
            if writers[writer_id].name != "N/A" and writer_id not in writers_set:
                movie_writers.append(writers[writer_id])
                writers_set.add(writer_id)

        actors = []
        if row[6] is not None and row[-2] is not None:
            actors = [
                Person(str(uuid.uuid4()), name)
                for _id, name in zip(row[6].split(","), row[-2].split(","))
                if name != "N/A"
            ]

        director = [Person(str(uuid.uuid4()), x.strip()) for x in row[2].split(",")] if row[2] != "N/A" else []
        people.extend(movie_writers + director + actors)

        movie_id = str(uuid.uuid4())
        imdb_rating = float(row[5]) if row[5] != "N/A" else None
        description = row[4] if row[4] != "N/A" else None
        movie = Movie(id=movie_id, title=row[3], imdb_rating=imdb_rating, description=description)

        genres = [Genre(str(uuid.uuid4()), genre) for genre in row[1].replace(" ", "").split(",")]
        movie_genres = {
            "genres": genres,
            "movie_id": movie_id,
        }
        movie_people = {
            "people": people,
            "movie_id": movie_id,
        }

        return {
            "movie": movie,
            "genres": genres,
            "movie_genres": movie_genres,
            "movie_people": movie_people,
        }

    def load_movies(self):
        """
        Основной метод для ETL.
        """
        records = []

        writers = self.load_writers_names()

        for row in self.conn.execute(self.SQL):
            transformed_row = self._transform_row(row, writers)
            records.append(transformed_row)

        return records
