import psycopg2

conn = psycopg2.connect(
    dbname="movies",
    user="postgres",
    host="localhost",
    password="postgres",
    port=5432,
    options="-c search_path=content",
)

with conn.cursor() as cur:
    cur.execute(
        """
    -- Фильм – заголовок, содержание, дата создания, возрастной ценз, режиссеры, актеры, сценаристы, жанры, ссылка.
        CREATE TABLE IF NOT EXISTS content.movies (
            id uuid PRIMARY KEY,
            title VARCHAR(255) UNIQUE NOT NULL,
            plot TEXT,
            creation_date DATE NOT NULL,
            rating VARCHAR (10)
            imdb_rating FLOAT,
            link VARCHAR(255) NOT NULL,
        );
    """
    )

    cur.execute(
        """
    -- Актер, Режиссер, Сценарист — Имя, фамилия, его фильмы
        CREATE TABLE IF NOT EXISTS content.people (
            id uuid PRIMARY KEY,
            first_name VARCHAR(45) NOT NULL,
            last_name VARCHAR(45) NOT NULL,
            role VARCHAR(45) NOT NULL,
        );
    """
    )

    cur.execute(
        """
    -- Промежуточная таблица для Movie/People
        CREATE TABLE IF NOT EXISTS content.movie_people (
            person_id uuid NOT NULL,
            movie_id uuid NOT NULL,
            FOREIGN KEY (person_id) REFERENCES content.people (id) ON UPDATE CASCADE,
            FOREIGN KEY (movie_id) REFERENCES content.movies (id) ON UPDATE CASCADE,
        );
    """
    )

    cur.execute(
        """
    -- Жанр — Описание
        CREATE TABLE IF NOT EXISTS content.genres (
            id serial PRIMARY KEY,
            genre VARCHAR(45) UNIQUE NOT NULL,
    );
    """
    )

    cur.execute(
        """
    -- Промежуточная таблица для Movie/Genre
        CREATE TABLE IF NOT EXISTS content.movie_genres (
            movie_id uuid NOT NULL,
            genre_id INT NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES content.movies (id) ON UPDATE CASCADE,
            FOREIGN KEY (genre_id) REFERENCES content.genres (id) ON UPDATE CASCADE,
        );
    """
    )
