# Standard library
import json
import os

# Third-party libraries
import bcrypt
from bottle import (
    Bottle, HTTPResponse, TEMPLATE_PATH, redirect, request, response,
    route, run, static_file, template
)
from bottle_login import LoginPlugin
from beaker.middleware import SessionMiddleware
from dotenv import load_dotenv
import psycopg2
from psycopg2 import Error, OperationalError, errors
from psycopg2.extras import RealDictCursor
import requests

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

SECRET_KEY = os.getenv("SECRET_KEY")
app = Bottle()
app.config['SECRET_KEY'] = SECRET_KEY
login_plugin = LoginPlugin()
app.install(login_plugin)

session_opts = {
    'session.type': 'memory',  
    'session.cookie_expires': True,
    'session.auto': True,
    'session.secret': SECRET_KEY  
}

class User:
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.name = username
        self.email = email

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

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

@app.route('/')
def root():
    """
    Renders SwipeFlix's homepage. (Alma) (Py)
    
    If the user is not logged in, it returns the public 'index' template.
    If the user is logged in, it returns a personalized welcome message.

    Returns:
        str: Rendered HTML content or welcome message.
    """
    current_user = login_plugin.get_user()
    name = current_user.name if current_user else None
    if not current_user:
        return template("index")  
    else:
        return template("index", name=name)

@app.route('/api/genres')
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

@app.route('/api/movies')
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

@app.route('/reg_page')
def reg_page():
    """ Renders the registration page containing a form. (Py)

    Returns:
        str: Rendered HTML content of the registration ('reg_page') template.
    """
    return template("reg_page")

@app.route('/login_page')
def login_page():
    """ Renders the login page containing a form. (Py)

    Returns:
        str: Rendered HTML content of the login ('login_page') template.
    """
    return template("login_page")

@app.route('/register', method=["GET", "POST"])
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


@app.route('/login', method=["GET", "POST"])
def login_user():
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
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, username, password_hash FROM users WHERE email = %s
                """, (email_input,))
                user_data = cursor.fetchone()
        
                if user_data:
                    hashed_pw = user_data['password_hash']

                    if bcrypt.checkpw(password_input.encode('utf-8'), hashed_pw.encode('utf-8')):
                        user = User(user_data['id'], user_data['username'], email_input)
                        login_plugin.login_user(user.id)
                        return redirect('/')
                    else:
                        return "Incorrect email or password"
                else:
                    return "Incorrect email or password"
    except psycopg2.Error as e:
        print(f"Databasfel vid inloggning: {e}")
        return template('login_page')

@login_plugin.load_user
def load_user_by_id(user_id):
    """Loads a user from the database by ID, used by bottle-login to restore sessions (Py)"""
    try:
        with get_db_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""SELECT id, username, email FROM users WHERE id = %s
                """, (user_id,))
                row = cursor.fetchone()
                if row:
                    return User(row['id'], row['username'], row['email'])
    except Exception as e:
        print(f"Fel vid laddning av användare: {e}")
    return None

@app.route('/register', method=["GET", "POST"]) #Denna funktion ska väl tas bort
def register_user_input():
    """Import registration information, hash the password and save to the database (Alma)"""

    if request.method == "GET":
        return template("register")  # renderar register.html

    new_user_email_input = request.forms.get('email')
    new_username_input = request.forms.get('username')
    new_password_input = request.forms.get('password')

    hashed_password = bcrypt.hashpw(new_password_input.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        with get_db_connection() as connection:  # Anslutningen öppnas här
            with connection.cursor() as cursor:  # Cursorn öppnas här
                # SQL-sats för att lägga till en ny användare
                cursor.execute('''
                    INSERT INTO users (email, username, password_hash)
                    VALUES (%s, %s, %s)
                ''', (new_user_email_input, new_username_input, hashed_password))
                
                # Spara ändringarna
                connection.commit()
                print(f"\nUser: {new_username_input} has been added to the DB")
    except Exception as error:
        print(f"Error occured when trying to add a Supplier: {error}")
    
    return redirect ("/")

@app.route('/logout')
def logout():
    login_plugin.logout_user()
    return redirect('/login')

@app.route('/static/<filename:path>')
def static_files(filename):
    """Sends back a static file (CSS, JavaScript or image)
    
    Args:
        filename (str): The name of the file the user is trying to access.

    Returns:
        HTTPResponse: The requested static file from the STATIC_DIR-folder.
    """
    return static_file(filename, root=STATIC_DIR)

app_with_sessions = SessionMiddleware(app, session_opts)

if __name__ == "__main__":
    run(app=app_with_sessions, host="localhost", port=8090, reloader=True)