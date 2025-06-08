# SwipeFlix
**SwipeFlix** är en filmrekommendationsapp där användare kan swipea höger för att gilla filmer likt Tinder. Applikationen bygger på data från [TMDb API](https://www.themoviedb.org/documentation/api) och användare kan skapa egna listor över sina favoritfilmer.

# Funktioner
* Användarinloggning med e-post, användarnamn och lösenord
* Hämtar filmdata från TMDb API
* Svepfunktion för att gilla eller hoppa över filmer
* Sparar gillade filmer i användarspecifika listor
* Backend med PostgreSQL för datalagring
* Lösenord ska hashas med bcrypt

# Teknik
* Frontend: HTML, CSS, JavaScript
* Backend: Python (Bottle)
* Databas: PostgreSQL
* API: TMDb
* Hantering av hemligheter: `python-dotenv`
* Paket: `psycopg2`, `bcrypt`, `requests`

# Installation
    1. **Klona projektet:**
    * https://github.com/swedishllama1/SwipeFlix01

    2. Skapa en .env fil med:
    TMDB_API_KEY=tmdb_nyckel
    DB_NAME=din_databas
    DB_USER=användarnamn
    DB_PASSWORD=lösenord
    DB_HOST=host.adress
    DB_PORT=5432
    *Dessa uppgifter kan erhållas separat från gruppen*

    3. Installera beroenden
    pip install -r requirements.txt

# Skapa tabellerna i pgAdmin 4
    Users
    CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
    );

    User_movies
    CREATE TABLE user_movies (
    id int NOT NULL DEFAULT nextval('user_movies_id_seq'::regclass),
    user_id INT,
    move_id INT NOT NULL,
    title text COLLATE pg_catalog."default",
    poster_path text COLLATE pg_catalog."default",
    liked boolean NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_movies_pkey PRIMARY KEY (id),
    CONSTRAINT user_movies_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
    )