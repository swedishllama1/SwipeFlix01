from bottle import route, run, template, static_file, request, redirect
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import OperationalError

load_dotenv()

tmdb_key = os.getenv("TMDB_API_KEY")

#Databaskoppling
def get_db_connection():
        """Skapar och retunerar en databasanslutning""" 
        try:
            connection = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
                )
            return connection
        except OperationalError as e:
             print(f"Could not connect to database:{e}")

if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        print("Anslutningen till databasen lyckades!")
        conn.close()
    else:
        print("Databasanslutning misslyckades.")

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
