# Standard library
import json
import os

# Third-party libraries
import bcrypt
from bottle import (
    Bottle, HTTPResponse, TEMPLATE_PATH, redirect, request, response,
    route, run, static_file, template
)
from dotenv import load_dotenv
import psycopg2
from psycopg2 import Error, OperationalError, errors
from psycopg2.extras import RealDictCursor
import requests

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
SECRET = os.getenv("COOKIE_SECRET")

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

def get_db_connection():
    """
    Establishes and returns a database connection. (Alma)

    Uses environment variables for host, port, dbname, user, and password.

    Returns:
        psycopg2.connect: A connection to a PostgreSQL database
        with RealDictCursor as a cursor.
    """
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        cursor_factory=RealDictCursor
    )

#Double check if the connection to the database works
if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        print("Connection successful!")
        conn.close()
    else:
        print("Connection unsuccessful!")

@route('/')
def root():
    """Renders SwipeFlix's homepage (Alma)
    
    Returns:
        str: Rendered HTML content of the 'index' template.
    """
    username = request.get_cookie("username", secret=os.getenv("COOKIE_SECRET"))
    return template("index", username=username)

@route('/api/genres')
def get_genres():
    """Fetches a list of movie genres from the TMDB API (Alma)
    
    Returns:
        dict: A JSON-file containing data of the genres from TMDB
    """
    url = f"{TMDB_BASE_URL}/genre/movie/list"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }
    r = requests.get(url, params=params)
    return r.json()

@route('/api/movies')
def get_movies():
    """Fetches movies from the TMDB API by genre or popularity (Alma)
    
    Query parameters:
        genre_id: The genre ID to filter movies by.
        page: The number of pages of results to fetch, default is 1.

    Returns:
        dict: A JSON-file containing movie data from TMDB.
    """

    genre_id = request.query.get('genre_id')
    page = request.query.get('page', default=1)
    if genre_id:
        url = f"{TMDB_BASE_URL}/discover/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "en-US",
            "page": page,
            "with_genres": genre_id
        }
    else:
        url = f"{TMDB_BASE_URL}/movie/popular"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "en-US",
            "page": page
        }
    r = requests.get(url, params=params)
    return r.json()

@route('/reg_page')
def reg_page():
    """ Renders the registration page containing a form. (Py)

    Returns:
        str: Rendered HTML content of the registration ('reg_page') template.
    """
    return template("reg_page")

@route('/login_page')
def login_page():
    """ Renders the login page containing a form. (Py)

    Returns:
        str: Rendered HTML content of the login ('login_page') template.
    """
    return template("login_page")

@route('/register', method=["GET", "POST"])
def register_user_input():
    """Handels user registration via GET and POST requests (Alma)
    
    GET: Renders the registration form where the user enters their email, chosen username and password.
    POST: Collects user input, hashes the password and saves the user to the database.

    Returns:
        str: The rendered registration template or a redirect to the homepage after a successful registration.
    """

    if request.method == "GET":
        return template("register")

    new_user_email_input = request.forms.get('email')
    new_username_input = request.forms.get('username')
    new_password_input = request.forms.get('password')

    hashed_password = bcrypt.hashpw(new_password_input.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO users (email, username, password_hash)
                    VALUES (%s, %s, %s)
                ''', (new_user_email_input, new_username_input, hashed_password))
                
                connection.commit()
                print(f"\nUser: {new_username_input} has been added to the DB")
    except Exception as error:
        print(f"Error occured when trying to register a new user: {error}")
    
    return redirect ("/")


@route('/login', method=["GET", "POST"])
def login():
    """Handles user login with GET and POST form requests (Py).
    This route renders a login form and processes user authentication.

    GET: Renders the login form where the user can enter email and password.
    POST: Validates the input, compares the hashed password against the database and redirects to the homepage if authentication is successful.
    
    Returns:
        str: The rendered login template (GET), a redirect to the homepage (successful login) or an error message string (failed login).
    """
    if request.method == "GET":
        return template("login_page")

    email_input = request.forms.get('email')
    password_input = request.forms.get('password')

    if not email_input or not password_input:
        return "Email and password are required."

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT username, password_hash FROM users WHERE email = %s
                """, (email_input,))
                user_data = cursor.fetchone()

                if user_data:
                    hashed_pw = user_data['password_hash']
                    if bcrypt.checkpw(password_input.encode('utf-8'), hashed_pw.encode('utf-8')):
                        response.set_cookie("username", user_data["username"], secret=os.getenv("COOKIE_SECRET"), path="/")
                        return redirect('/')
                    else:
                        return "Incorrect email or password"
                else:
                    return "Incorrect email or password"
    except psycopg2.Error as e:
        print(f"Databasfel vid inloggning: {e}")
        return template('login_page')
    

@route('/like', method='POST')
def like_movie():
    username = request.get_cookie("username", secret=os.getenv("COOKIE_SECRET"))
    print("===> COOKIE username:", username)

    if not username:
        return HTTPResponse(status=401, body="Ingen användare inloggad")

    data = request.json
    print("===> INKOMMANDE JSON:", data)

    movie_id = data.get("id")
    title = data.get("title")
    poster_path = data.get("poster_path")

    if not movie_id or not title:
        print("===> Fel: saknar id eller title")
        return HTTPResponse(status=400, body="Incomplete movie data")

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Hämta användarens ID
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                print("===> User från DB:", user)

                if not user or not user.get("id"):
                    return HTTPResponse(status=404, body="Användare saknas")

                # Spara filmen
                cursor.execute("""
                    INSERT INTO user_movies (user_id, movie_id, title, poster_path, liked)
                    VALUES (%s, %s, %s, %s, TRUE)
                """, (user["id"], movie_id, title, poster_path))

                conn.commit()
                print("===> Film sparad")

        return {"message": "Film gillad och sparad"}
    except Exception as e:
        print("===> Fel vid INSERT:", e)
        return HTTPResponse(status=500, body="Server error")


@route('/user_profile')
def user_profile():
    """ Renders the user profile containing user information and liked movies. (Py)

    Returns:
        str: Rendered HTML content of the user profile ('user_profile') template.
    """
    username = request.get_cookie("username", secret=os.getenv("COOKIE_SECRET"))
    user_email = None
    
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT email FROM users WHERE username = %s", (username,))
                result = cursor.fetchone()
                if result:
                    user_email = result['email']
    except Exception as e:
        print(f"Error fetching email: {e}")
        import traceback
        traceback.print_exc()
    
    return template("user_profile", username=username, user_email=user_email)

@route('/logout')
def logout():
    """Logs out the user by deleting the username cookie and redirects to the homepage. (Alma)
    
    Returns:
        str: A redirect that renders the homepage as the user logs out.
    """
    response.delete_cookie("username", path="/")
    return redirect("/")

@route('/api/liked')
def get_liked_movies():
    username = request.get_cookie("username", secret=os.getenv("COOKIE_SECRET"))
    if not username:
        return HTTPResponse(status=401, body="Inte inloggad")

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                if not user:
                    return HTTPResponse(status=404, body="Användare hittades inte")

                cursor.execute("""
                    SELECT title, poster_path
                    FROM user_movies
                    WHERE user_id = %s AND liked = TRUE
                    ORDER BY timestamp DESC
                """, (user["id"],))
                movies = cursor.fetchall()

        return {"movies": movies}
    except Exception as e:
        print("Fel vid hämtning av gillade filmer:", e)
        return HTTPResponse(status=500, body="Serverfel")

@route('/static/<filename:path>')
@route('/static/<filename>')
def static_files(filename):
    """Sends back a static file (CSS, JavaScript or image)
    
    Args:
        filename (str): The name of the file the user is trying to access.

    Returns:
        HTTPResponse: The requested static file from the STATIC_DIR-folder.
    """
    return static_file(filename, root=STATIC_DIR)


run(host="localhost", port=8090, reloader=True)
