from bottle import route, run, template, static_file, request, redirect

#Databaskoppling

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