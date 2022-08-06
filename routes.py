
from flask import render_template, request, redirect, session, abort
from app import app
import users


@app.route("/")
def index():
    alcohols_count = alcohols.count()
    #return render_template("index.html", name=users.username(), a_amount=alcohols_count)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        error_name, error_match, error_length = "", "", ""
        if password1 != password2:
            error_match = "Salasanat eivät täsmää"
        if users.is_taken(username.lower()):
            error_name = "Käyttäjänimi on jo varattu"
        if len(password1) < 7 or len(password1) > 35:
            error_length = "Salasanan oltava 8-35 merkin mittainen. "
        if error_name != "" or error_length != "" or error_match != "":
            return render_template("register.html", e_name=error_name, e_match=error_match,
                                   e_length=error_length, name=username)
        if users.register(username.lower(), password1):
            return redirect("/welcome_page")
        else:
            return render_template("register.html",
                                   e_name="Rekisteröinti ei onnistunut")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/welcome")
        else:
            return render_template("login.html", error="Väärä käyttäjätunnus tai salasana")

@app.route("/welcome")
def welcome():
    return render_template("welcome_page.html", name=users.username())