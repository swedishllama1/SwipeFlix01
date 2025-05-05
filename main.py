from bottle import route, run, template, static_file, request, redirect
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import OperationalError, Error
import os

# Standard library imports
from dotenv import load_dotenv

# Third-party imports
from bottle import (
    route, run, template, request, static_file,
    response, redirect, HTTPResponse, TEMPLATE_PATH
)
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import errors
import bcrypt
import requests
import json

# Load environment variables and configure templates
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_PATH.insert(0, os.path.join(BASE_DIR, 'views'))
load_dotenv()

API_KEY = os.getenv('API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

load_dotenv()

tmdb_key = os.getenv("TMDB_API_KEY")

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
        print("✅ Anslutningen till databasen lyckades!")
        conn.close()
    else:
        print("❌ Databasanslutning misslyckades.")

####
"""Provar om api-nyckeln kan döljas från javascript-filen"""

@route('/api/genres')
def get_genres():
    tmdb_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=en-US"
    r = requests.get(tmdb_url)
    response.content_type = 'application/json'
    return r.content

####

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



@route('/')
def index():
    return template("index")
    #Om användaren redan är inloggad så visa bara en logga ut knapp i högra hörnet

@route('/static/<filename>')
def static_files(filename):
    return static_file(filename, root="STATIC")
####

run(host="127.0.0.1", port=8090, reloader=True) #Detta kan såklart ändras, fråga gruppen
