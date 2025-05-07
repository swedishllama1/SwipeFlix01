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
    Create and return a new database connection.

    Uses environment variables for host, port, dbname, user, and password.
    The cursor_factory is set to RealDictCursor for dict-like fetches.

    :return: psycopg2 connection object
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
@route('/')              # gratis redirect så du slipper skriva /start
def root():
    return redirect('/start')

@route('/start')
def index():
    return static_file("testindex.html", root=BASE_DIR) 

@route('/api/genres')
def get_genres():
    url = f"{TMDB_BASE_URL}/genre/movie/list"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }
    r = requests.get(url, params=params)
    return r.json()

@route('/api/movies')
def get_movies():
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

@route('/start')
def index():
    full_path = os.path.join(BASE_DIR, "testindex.html")
    print("→ försöker skicka:", full_path, os.path.exists(full_path))
    return static_file("testindex.html", root=BASE_DIR)
####


"""Skapade routes in-progress"""
@route('/auth_panel')
def auth_panel():
    return template("auth_panel")

@route('/login', method="post")
def login():
    email = request.forms.get('email')
    username = request.forms.get('username')
    password = request.forms.get('password')
    #Kolla om användaren finns i databasen såfall:
        #redirect('/')
    #Om inte: visa medelande att användaren inte finns    

@route('/register')
def register_new_user_input():
    """INTE KLAR"""
    
    user_input_email = getattr(request.forms, "title")
    user_input_username = getattr(request.forms, "content")
    user_input_password = getattr(request.forms, "content")

    articles.append({
        "id" : article_id,
        "title" : input_title,
        "content" : input_content
    })

    my_file = open("articles.json", "w")
    my_file.write(json.dumps(articles, indent=4))
    my_file.close()

    redirect("/")

    return template("reg")

@route('/register', method=["GET", "POST"])
def register_user_input():
    if request.method == "GET":
        return template("register")  # renderar register.html

    new_user_email_input = request.forms.get('email')
    new_username_input = request.forms.get('username')
    new_password_input = request.forms.get('password')

    try:
        with get_db_connection() as connection:  # Anslutningen öppnas här
            with connection.cursor() as cursor:  # Cursorn öppnas här
                # SQL-sats för att lägga till en leverantör
                cursor.execute('''
                    INSERT INTO users (email, username, password_hash)
                    VALUES (%s, %s, %s)
                ''', (new_user_email_input, new_username_input, new_password_input))
                
                # Spara ändringarna
                connection.commit()
                print(f"\nUser: {new_username_input} have been added to the DB")
    except Exception as error:
        print(f"Error occured when trying to add a Supplier: {error}")


@route('/static/<filename>')
def static_files(filename):
    return static_file(filename, root=STATIC_DIR)
####

run(host="localhost", port=8090, reloader=True) #Detta kan såklart ändras, fråga gruppen
