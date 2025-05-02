from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

tmdb_key = os.getenv("TMDB_API_KEY")

def get_db_connection():
        """Skapar och retunerar en databasanslutning"""
        return psycopg2.connect (
        dbname="aa_swipeflix",  # database name
        user="aq1770",  # enter username
        password="X0c5vfzn",  # enter password
        host="pgserver.mau.se",  # enter database host
        port="5432"  # standardporten för PostgreSQL
    )