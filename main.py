from bottle import route, run, template, static_file, request, redirect
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

tmdb_key = os.getenv("TMDB_API_KEY")

#Databaskoppling
def get_db_connection():
        """Skapar och retunerar en databasanslutning"""
        return psycopg2.connect (
        dbname="aa_swipeflix",  # database name
        user="aq1770",  # enter username
        password="X0c5vfzn",  # enter password
        host="pgserver.mau.se",  # enter database host
        port="5432"  # standardporten för PostgreSQL
    )

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
