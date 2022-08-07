
from flask import render_template, request, redirect
from app import app
import users as users
import alcohols
import tags as tags


@app.route("/")
def index():
    count = alcohols.count()
    return render_template("index.html", name=users.username(), a_amount=count)

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




@app.route("/alcohols", methods=["GET", "POST"])
def alcohols():
    if request.method == "POST":
        alcohols = alcohols.get_all()
        heading = "Kaikki alkoholit:"
        tag_list = tags.tags_all()
        if "search" in request.form:
            alc = request.form["alcohol"].lower()
            if len(alc):
                alc_id = alcohols.get_alcohol(alc)
                alcohols_cont_alc = []
                for aid in alc_id:
                    alcohols_cont_alc += alcohols.get_alcohol(aid.id)
                return render_template("alcohols.html", alcohols=alcohols_cont_alc,
                                       tags=tag_list, list_heading="Alkoholit, joiden nimessä'"
                                       + str(alc)+"':")
            if len(alc) > 0:
                return render_template("alcohols.html",
                                       error="Ei tuloksia hakusanalla '" + str(alc)+"'",
                                       list_heading="Kaikki Alkoholit:", alcohols=alcohols,
                                       tags=tag_list)
        if "Alphabetical" in request.form:
            heading = "Kaikki alkoholit aakkkosjärjestyksessä:"
        if "Anew" in request.form:
            alcohols = alcohols.all_order_novelty()
            heading = "Uusin alkoholi ensin:"
        if "Apopular" in request.form:
            alcohols = alcohols.all_order_by_favorite()
            heading = "Suosituin alkoholi ensin:"
        for tag in tag_list:
            if tag[0] in request.form:
                alcohols = alcohols.all_with_tag(tag[0])
                heading = "Alkoholit kategoriassa "+tag[0]+":"
        return render_template("alcohols.html", list_heading=heading, alcohols=alcohols, tags=tag_list)
    if request.method == "GET":
        alcohols = alcohols.get_all()
        heading = "Kaikki alkoholit:"
        tag_list = tags.tags_all()
        return render_template("alcohols.html", list_heading=heading, alcohols=alcohols, tags=tag_list)


@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")