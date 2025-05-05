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

#Databaskoppling
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
"""if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        print("✅ Anslutningen till databasen lyckades!")
        conn.close()
    else:
        print("❌ Databasanslutning misslyckades.")"""

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


@route('/register', method="post")
def register():
    email = request.forms.get('email')
    username = request.forms.get('username')
    password = request.forms.get('password')
    #Kolla om användaren finns i databasen, om inte:
        #Lägg till användarinformation i databasen
        #redirect('/')
    #Om användaren finns visa medelande att användaren redan finns

@route('/')
def index():
    return template("index")
    #Om användaren redan är inloggad så visa bara en logga ut knapp i högra hörnet

@route('/static/<filename>')
def static_files(filename):
    return static_file(filename, root="STATIC")

run(host="127.0.0.1", port=8090, reloader=True) #Detta kan såklart ändras, fråga gruppen
