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
            CREATE SCHEMA IF NOT EXISTS content;
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS content.movies (
            id uuid PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            plot TEXT,
            creation_date DATE NOT NULL,
            mpa_film_rating VARCHAR (10)
            imdb_rating FLOAT,
            link VARCHAR(255) NOT NULL,
        );
    """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS content.people (
            id uuid PRIMARY KEY,
            first_name VARCHAR(45) NOT NULL,
            last_name VARCHAR(45) NOT NULL,
        );
    """
    )

    cur.execute(
        """
        CREATE TYPE person_roles AS ENUM ('Actor','Director', 'Writer');
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS content.roles (
            id serial PRIMARY KEY,
            role person_roles DEFAULT 'Actor' NOT NULL,
        );
    """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS content.movie_people (
            person_id uuid NOT NULL,
            movie_id uuid NOT NULL,
            UNIQUE (movie_id, person_id)
            FOREIGN KEY (person_id) REFERENCES content.people (id) ON UPDATE CASCADE,
            FOREIGN KEY (movie_id) REFERENCES content.movies (id) ON UPDATE CASCADE,
            FOREIGN KEY (role_id) REFERENCES content.roles (id)
        );
    """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS content.genres (
            id serial PRIMARY KEY,
            genre VARCHAR(45) UNIQUE NOT NULL,
    );
    """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS content.movie_genres (
            movie_id uuid NOT NULL,
            genre_id INT NOT NULL,
            UNIQUE (movie_id, genre_id)
            FOREIGN KEY (movie_id) REFERENCES content.movies (id) ON UPDATE CASCADE,
            FOREIGN KEY (genre_id) REFERENCES content.genres (id) ON UPDATE CASCADE,
        );
    """
    )
