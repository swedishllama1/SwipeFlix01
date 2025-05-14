from bottle import Bottle, static_file, route, run, template, static_file, request, redirect, response, HTTPResponse, TEMPLATE_PATH
from bottle import route, run
from bottle import Bottle

from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError, Error, errors
from psycopg2.extras import RealDictCursor
import bcrypt
import requests
import json

import os

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")   # gemener
INDEX_FILE = os.path.join(BASE_DIR, "testindex.html")

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

#Database connection
def get_db_connection():
    """
    Create and return a new database connection. (Alma)

    Uses environment variables for host, port, dbname, user, and password.
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

####
#Testar göra en ny startsida som anropar API:et
####
@route('/')
def root():
    """Rendering SwipeFlixes homepage (Alma)"""
    return template("index")

@route('/api/genres')
def get_genres():
    """Import genres from API (Alma)"""
    url = f"{TMDB_BASE_URL}/genre/movie/list"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }
    r = requests.get(url, params=params)
    return r.json()

@route('/api/movies')
def get_movies():
    """Import movies from API (Alma)"""

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

####


"""Skapade routes in-progress"""
@route('/reg_page')
def reg_page():
    return template("reg_page")

@route('/login_page')
def login_page():
    return template("login_page")

@route('/login', method=["GET", "POST"])
def login():
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
                    SELECT password_hash FROM users WHERE email = %s
                """, (email_input,))
                user_password = cursor.fetchone()

                if user_password:
                    hashed_pw = user_password['password_hash']
                    if bcrypt.checkpw(password_input.encode('utf-8'), hashed_pw.encode('utf-8')):
                        return redirect('/')
                    else:
                        return "Incorrect email or password"
                else:
                    return "Incorrect email or password"
    except psycopg2.Error as e:
        print(f"Databasfel vid inloggning: {e}")
        return template('login_page')



@route('/register', method=["GET", "POST"])
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


@route('/static/<filename:path>')
def static_files(filename):
    return static_file(filename, root=STATIC_DIR)
####

run(host="localhost", port=8090, reloader=True) #Detta kan såklart ändras, fråga gruppen
