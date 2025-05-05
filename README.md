# SwipeFlix
**SwipeFlix** är en filmrekommendationsapp där användare kan swipea höger för att gilla filmer likt Tinder. Applikationen bygger på data från [TMDb API](https://www.themoviedb.org/documentation/api) och användare kan skapa egna listor över sina favoritfilmer.

# Funktioner
* Användarinloggning med e-post, användarnamn och lösenord
* Hämtar filmdata från TMDb API
* Svepfunktion för att gilla eller hoppa över filmer
* Sparar gillade filmer i användarspecifika listor
* Backend med PostgreSQL för datalagring
* Lösenord ska hashas med bcrypt

# Teknik
* Frontend: HTML, CSS, JavaScript
* Backend: Python (Bottle)
* Databas: PostgreSQL
* API: TMDb
* Hantering av hemligheter: `python-dotenv`
* Paket: `psycopg2`, `bcrypt`, `requests`

# Installation
    1. **Klona projektet:**
    * https://github.com/swedishllama1/SwipeFlix01

    2. Skapa en .env fil med:
    TMDB_API_KEY=tmdb_nyckel
    DB_NAME=din_databas
    DB_USER=användarnamn
    DB_PASSWORD=lösenord
    DB_HOST=host.adress
    DB_PORT=5432
    *Dessa uppgifter kan erhållas separat från gruppen*

    3. Installera beroenden
    pip install -r requirements.txt