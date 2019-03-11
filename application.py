import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from flask import Flask, jsonify, render_template, request, url_for
from flask_jsglue import JSGlue
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from passlib.apps import custom_app_context as pwd_context
from helpers import apology, login_required, lookup, usd
from datetime import datetime, date, time
from flask import Flask, redirect, render_template, request, url_for
import helpers
import os
import sys

# Ensure environment variable is set

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True




# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///potrcko.db")

@app.route("/")
@login_required
def articles():

    per_page = 9

    art = db.execute("SELECT * FROM articles ")

    num_rows = 0
    for a in art:
        num_rows = num_rows + 1

    total_len = (int)(num_rows / per_page)

    is_admin = db.execute("SELECT is_admin FROM users WHERE id = :id", id = session["user_id"])
    cart = db.execute("SELECT * FROM cart WHERE id = :id", id = session["user_id"])


    sum_of_pr = 0
    i = 0
    for article in cart:
       sum_of_pr += cart[i]["price"] * cart[i]["quantity"]
       i = i + 1

    if is_admin[0]["is_admin"] == 1:
        return render_template("articles_admins.html", articles = art, total = total_len)
    else:
        return render_template("articles_users.html", articles = art, cart = cart, total = total_len, per_page = per_page, bill = sum_of_pr)


@app.route("/addToCart", methods=['POST'])
def addToCart():

    article = request.form['product_name']

    art_from_base = db.execute("SELECT name, price FROM articles WHERE name = :name", name = article)

    if art_from_base != None:

         is_in_base = db.execute("SELECT * FROM cart WHERE name = :art", art = art_from_base[0]["name"])

         if len(is_in_base) > 0:
            inc_quantity = is_in_base[0]["quantity"] + 1
            db.execute("UPDATE cart SET quantity = :quantity WHERE name = :name", quantity = inc_quantity, name = article)
         else:
            db.execute("INSERT INTO cart(id, name, price) VALUES (:id, :name, :price)", id = session["user_id"], name = art_from_base[0]["name"], price = art_from_base[0]["price"])

    return jsonify({'success' : 'Success!'})

@app.route("/getArticleFromDb", methods=['POST'])
def getArticleFromDb():
    name = request.form['name']
    slcArticle = db.execute("SELECT * FROM articles WHERE name = :name", name = name)

    id = slcArticle[0]["id"]

    return jsonify({'id' : id, 'name' : slcArticle[0]['name'], 'price' : slcArticle[0]['price'], 'desc' : slcArticle[0]['description'], 'image' : slcArticle[0]['image'], 'is_available' : slcArticle[0]['is_available']})

@app.route("/saveChangesOnArticle", methods=['POST'])
def saveChangesOnArticle():
    id = request.form['id']
    name = request.form['name']
    price = request.form['price']

    desc = request.form['desc']
    image = request.form['image']
    is_available = request.form['is_available']

    db.execute("UPDATE articles SET name = :name, price = :price, description = :description, image = :image, is_available = :is_available WHERE id = :id", id = id, name = name, price = price, description = desc, image = image, is_available = is_available)

    return jsonify({'success' : 'Izmena je uspesna!'})

@app.route("/removeArticle", methods=['POST'])
def removeArticle():
    name = request.form['name']

    db.execute("DELETE * FROM articles WHERE name = :name", name = name)

    return jsonify({'success' : 'Proizvod je uklonjen!'})

@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():

    cart = db.execute("SELECT * FROM cart WHERE id = :id", id = session["user_id"])

    booy = db.execute("SELECT * FROM buy WHERE id = :id", id = session["user_id"])

    sum_of_pr = 0
    i = 0
    for article in cart:
       sum_of_pr += cart[i]["price"] * cart[i]["quantity"]
       i = i + 1

    return render_template("cart.html", cart=cart, bill=sum_of_pr, buy=booy)

@app.route("/complete_buy", methods=['POST'])
def complete_buy():

    cena = request.form['price']
    vreme = request.form['time']

    db.execute("INSERT INTO buy (id, price, date ) VALUES (:id, :cena, :vreme)", id = session["user_id"], cena = cena, vreme = vreme)

    db.execute("DELETE FROM cart WHERE id= :id ", id=session["user_id"])

    return jsonify({'notice' : 'Uspesno ste izvrsili kupovinu!'})

@app.route("/refuse_buy", methods=['POST'])
def refuse_buy():

    rows=db.execute("DELETE FROM cart WHERE id= :id ", id=session["user_id"])

    if rows != None:
        return jsonify({'notice' : 'Uspesno ste odustali!'})

    return jsonify({'notice' : 'Neuspesno ste zavrsili nekupovinu!'})

@app.route("/impressions", methods=["GET", "POST"])
@login_required
def impression():

    impressions = db.execute("SELECT * FROM impressions")

    if request.method == "POST":
        return render_template("impressions.html", impressions = impressions)

    return render_template("impressions.html", impressions = impressions)

@app.route("/post_impression", methods=['POST'])
def post_impression():

    cena = request.form['price']
    kvalitet = request.form['quality']
    brzina = request.form['speed']
    komentar = request.form['comment']

    #DA LI JE OSTAVLJEN POZITIVAN ILI NEGATIVAN KOMENTAR
    positives = os.path.join(sys.path[0], "positive-words.txt")
    negatives = os.path.join(sys.path[0], "negative-words.txt")

    positivni = []
    negativni = []

    # prolazimo kroz svau pojedinacnu liniju fajla
    with open(positives) as lines:
        for line in lines:
            for word in line.split():
                positivni.append(word)

    #isti proces kao i kod pozitivnih reci
    with open(negatives) as lines:
        for line in lines:
            negativni.append(line.strip("\n"))

    # get screen_name's tweets
    tweets = komentar.split()

    positivne=0
    negativne=0
    neutralne=0
    score = 0

    # Prolazimo kroz poruku
    for tw in tweets:
        #proveravamo da li se rec iz tweet-a nalazi u pozitivnim, ako se nalazi onda ide +1
        if tw.lower() in positivni:
            score += 1
        #proveravamo da li se rec iz tweet-a nalazi u negativnim, ako se nalazi onda ide -1
        elif tw.lower() in negativni:
            score -= 1

    if score > 0:
        positivne = 1
    elif score < 0:
        negativne = 1
    else:
        neutralne = 1

    if positivne == 1 or neutralne == 1:
        db.execute("INSERT INTO impressions (id, comment, quality, speed, price) VALUES (:id, :comment, :quality, :speed, :price)", id = session["user_id"], comment = komentar, quality = kvalitet, speed = brzina, price = cena)
        return jsonify({'notice' : 'Uspesno ste ocenili nasu uslugu!'})
    else:
        return jsonify({'notice' : 'Vaš komentar je isuviše negativan/vulgaran, papir trpi svakakve reči ali naša baza ne mora! Nakon provere cemo razmotriti njegovo objavljivanje :)'})

@app.route("/career")
@login_required
def career():

    fakulteti=["FTN", "PMF", "Filozofski", "Medicinski", "Poljoprivredni" ,"Tehnološki", "Pravni", "DIF", "VPŠ"]

    return render_template("career.html", fakulteti=fakulteti)

@app.route("/apply_for_student_job", methods=['POST'])
def apply_for_student_job():

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    message = request.form['message']
    profession = request.form['profession']
    birth_year = request.form['birth_year']
    faculty = request.form['faculty']

    db.execute("INSERT INTO studentJobs (id, first_name, last_name, email, message, profession, birth_year, faculty) VALUES (:id, :first_name, :last_name, :email, :message, :profession, :birth_year, :faculty)", id = session["user_id"], first_name = first_name, last_name = last_name, email = email, message = message, profession = profession, birth_year = birth_year, faculty = faculty)

    return jsonify({"success" : "Uspelo je!"})

@app.route("/apply_for_operator_job", methods=['POST'])
def apply_for_operator_job():

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    message = request.form['message']
    birth_year = request.form['birth_year']

    db.execute("INSERT INTO operatorJobs (id, first_name, last_name, email, birth_year, message) VALUES (:id, :first_name, :last_name, :email, :birth_year, :message)", id = session["user_id"], first_name = first_name, last_name = last_name, email = email, message = message, birth_year = birth_year)

    return jsonify({"success" : "Uspelo je!"})


@app.route("/partner")
@login_required
def partner():

    return render_template("partner.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

   # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        id = request.form['id']
        # Remember which user has logged in
        session["user_id"] = id

        return jsonify({"success" : "Korisnik se uspesno prijavio"})

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/check_login", methods=['POST'])
def check_login():

    user = request.form['username']
    users = db.execute("SELECT * FROM users WHERE username = :username", username = user)

    if len(users) != 1:
        return jsonify({'info' : 'Korisnik ne postoji!'})

    passw = request.form['password']

    if not pwd_context.verify(passw, users[0]["hash"]):
        return jsonify({'info' : 'Uneli ste pogresnu lozinku!'})

    return jsonify({'info' : users[0]["id"]})

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    #session.clear()

     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Dodajemo novog korisnika u bazu podataka

        id = request.form['id']
        # Remember which user has logged in
        session["user_id"] = id

        return jsonify({'info' : 'Uspesno ste se registrovali!'})

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/check_register", methods=['POST'])
def check_register():

    user = request.form['username']
    users = db.execute("SELECT * FROM users WHERE username = :username", username = user)

    if len(users) == 1:
        return jsonify({'info' : 'Korisnik vec postoji!'})

    passw = request.form['password']
    passwConf = request.form['passConf']

    if passw != passwConf:
        return jsonify({'info' : 'Lozinke se ne poklapaju!'})

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    address = request.form['address']
    email = request.form['email']
    ph_num = request.form['ph_num']

    new_user = db.execute("INSERT into users (username, hash, first_name, last_name, phone, address, email) VALUES (:username, :hash, :first_name, :last_name, :phone, :address, :email)", username = user, hash=pwd_context.hash(passw), first_name = first_name, last_name = last_name, phone = ph_num, address = address, email = email)
    nw_u = db.execute("SELECT * from users WHERE username = :username", username = user)

    return jsonify({'info' : nw_u[0]['id']})


@app.route("/about", methods=["GET", "POST"])
@login_required
def about():

    if request.method == "POST":

        return redirect("/")

    else:
        return render_template("about.html")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

@app.route("/password", methods=["GET", "POST"])
def password():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        new_password = pwd_context.hash(request.form.get("new_password"))

        #iscitavamo iz baze staru lozinku
        hashes = db.execute("SELECT hash FROM users WHERE id = :user_id", user_id=session["user_id"])

        #proveravamo da li se stara lozinka poklapa sa unetom starom lozinkom
        if not pwd_context.verify(request.form.get("old_password"), hashes[0]['hash']):
             return apology("Old passwords do not match", 403)

        # apdejtujemo stari password novim
        db.execute("UPDATE users SET hash = :hash WHERE id=:id", hash=pwd_context.hash(request.form.get("new_password")),id=session['user_id'] )

        return redirect("/")

    else:
        return render_template('password.html')

