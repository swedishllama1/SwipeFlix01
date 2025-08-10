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
    TMDB_API_KEY=tmdb_key
    DB_NAME=your_database
    DB_USER=username
    DB_PASSWORD=password
    DB_HOST=host.adress
    DB_PORT=5432
    *These credentials are to be obtained separately from the group to maintain the security of the credentials. They must be manually switched out by the user to the correct credentials in order for the program to function. Please see the attached document titled "ENV INFO".*

    3. Install dependencies
    pip install -r requirements.txt
    *This command could possibly look different for each individuall user, for example, for group member Alma - the command looks like this: py -m pip install -r requirements.txt
    
    Should any of the packages fail to install, consider looking up permissions and instructions online for the respective packages.*

# Create tables in pgAdmin 4
1)    Users
    CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
    );

2)    User_movies
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

3)    Liked_movies
    CREATE TABLE liked_movies(
    id integer NOT NULL DEFAULT nextval('liked_movies_id_seq'::regclass),
    user_id integer NOT NULL,
    movie_id integer NOT NULL,
    liked_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT liked_movies_pkey PRIMARY KEY (id),
    CONSTRAINT liked_movies_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        )
    
4)    Shown_movies
    CREATE TABLE shown_movies(
    id integer NOT NULL DEFAULT nextval('shown_movies_id_seq'::regclass),
    user_id integer NOT NULL,
    movie_id integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    poster_path text COLLATE pg_catalog."default",
    title text COLLATE pg_catalog."default",
    CONSTRAINT shown_movies_pkey PRIMARY KEY (id),
    CONSTRAINT shown_movies_user_id_movie_id_key UNIQUE (user_id, movie_id),
    CONSTRAINT shown_movies_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
    
    (The tables were fetched by right-clicking the table > Scripts > Create Script in pgAdmin4
    Therefore some metadata has been added, which is why the tables may look funky.)

# Run the program by navigating to the "main.py" file in Visual Studio Code and pressing "Run Python file", thereafter observe the command-box at the bottom of the screen in the same program, and open the link: "http://localhost:8090/" by holding the Ctrl button and clicking on it with your mouse.