# SwipeFlix
**SwipeFlix** is a movie recommendation app where users can swipe right to like movies, similar to Tinder. The app is based on data from the [TMDb API](https://www.themoviedb.org/documentation/api) and users can create their own lists of favorite movies.

# Funktioner
* User login with email, username, and password
* Fetches movie data from the TMDb API
* Swipe functionality to like or skip movies
* Saves liked movies in user-specific lists
* Backend with PostgreSQL for data storage
* Passwords are hashed using bcrypt

# Teknik
* Frontend: HTML, CSS, JavaScript
* Backend: Python (Bottle)
* Database: PostgreSQL
* API: TMDb
* Secret management: `python-dotenv`
* Packages: `psycopg2`, `bcrypt`, `requests`

# Installation
    1. **Clone the project**
    https://github.com/swedishllama1/SwipeFlix01

    2. Create a .env file with the following:
    TMDB_API_KEY=tmdb_nyckel
    DB_NAME=din_databas
    DB_USER=användarnamn
    DB_PASSWORD=lösenord
    DB_HOST=host.adress
    DB_PORT=5432
    *These credentials can be obtained separately from the group.*

    3. Install dependencies
    pip install -r requirements.txt

# Create tables in pgAdmin 4
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
    
    (User_movies table was fetched by right-clicking the table > Scripts > Create Script
    Therefore some metadata has been added)