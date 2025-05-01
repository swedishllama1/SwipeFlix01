from dotenv import load_dotenv
import os

load_dotenv()

tmdb_key = os.getenv("TMDB_API_KEY")
print(f"API-nyckel: {tmdb_key}")