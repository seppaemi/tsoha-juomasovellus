from app import app
from flask import render_template, request, redirect, session
from db import db
import users
import alcohols
import reviews


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    msg = "Hakemaasi sivua ei löytynyt."
    return render_template("error.html", error=msg), 404


@app.route("/all-alcs", methods=["GET", "POST"])
def all_alcohols():
    tags = alcohols.list_tags()
    if request.method == "GET":
        results = alcohols.list_alcohols()
        return render_template("all-alcohols.html", tags=tags, results=results)
    if request.method == "POST":
        tag_id = request.form["tag"]
        results = alcohols.list_alcohols(tag_id)
        return render_template("all-alcohols.html", tags=tags, results=results)


@app.route("/search")
def search():
    keyword = request.args["keyword"]
    sortby = request.args["sortby"]
    orderby = request.args["orderby"]
    results = alcohols.search(keyword, sortby, orderby)
    return render_template("result.html", results=results, keyword=keyword, sortby=sortby, orderby=orderby)


@app.route("/alc/<int:id>")
def alcohol(id):
    alc, msg = alcohols.get_alcohol(id)
    if not alc:
        return render_template("error.html", error=msg)
    creator = users.get_username(alc[1])
    ingredients = alcohols.get_alcohol_ingredients(id)
    tags = alcohols.get_alcohol_tags(id)
    favourite = alcohols.is_favourite(id)
    average = reviews.get_average(id)
    comments = reviews.get_comments(id)
    return render_template("alcohol.html", creator=creator, alcohol=alcohol, tags=tags,
                           ingredients=ingredients, comments=comments,
                           average=average, favourite=favourite)


@app.route("/add-alc", methods=["GET", "POST"])
def add_alcohol():
    if request.method == "GET":
        tags = alcohols.list_tags()
        return render_template("new-alcohol.html", tags=tags)
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            return render_template("error.html", error="Toiminto ei ole sallittu.")
        title = request.form["title"]
        description = request.form["description"]
        instruction = request.form["instruction"]
        ingredients = request.form.getlist("ingredient")
        tags = request.form["tag"]
        add_ok, msg, alcohol_id = alcohols.add_alcohol(title, description,
                                                    instruction, ingredients, tags)
        if not add_ok:
            return render_template("error.html", error=msg)
        return redirect(f"/alc/{alcohol_id}")


@app.route("/modify-alc/<int:id>")
def modify_alcohol(id):
    alc, msg = alcohols.get_alcohol(id)
    if not alc:
        return render_template("error.html", error=msg)
    own_alc, msg = alcohols.is_own_alcohol(id)
    if not own_alc:
        return render_template("error.html", error=msg)
    ingredients = alcohols.get_alcohol_ingredients(id)
    alcoholtags = [t[0] for t in alcohols.get_alcohol_tags(id)]
    tags = alcohols.list_tags()
    return render_template("modify-alcohol.html", alc=alc,
                           ingredients=ingredients, tags=tags, alcoholtags=alcoholtags)


@app.route("/execute-modification", methods=["POST"])
def execute_modification():
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="Toiminto ei ole sallittu.")
    alcohol_id = request.form["alcohol_id"]
    own_alc, msg = alcohols.is_own_alcohol(alcohol_id)
    if not own_alc:
        return render_template("error.html", error=msg)
    title = request.form["title"]
    description = request.form["description"]
    instruction = request.form["instruction"]
    ingredients = request.form.getlist("ingredient")
    tags = request.form.getlist("tag")
    modify_ok, msg = alcohols.modify_alcohol(alcohol_id, title, description,
                                           instruction, ingredients, tags)
    if not modify_ok:
        return render_template("error.html", error=msg)
    return redirect(f"/alc/{alcohol_id}")


@app.route("/add-favourite", methods=["POST"])
def add_favourite():
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="Toiminto ei ole sallittu.")
    alcohol_id = request.form["alcohol_id"]
    add_ok, msg = alcohols.add_favourite(alcohol_id)
    if not add_ok:
        return render_template("error.html", error=msg)
    return redirect(f"/alc/{alcohol_id}")


@app.route("/delete-favourite", methods=["POST"])
def delete_favourite():
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="Toiminto ei ole sallittu.")
    alcohol_id = request.form["alcohol_id"]
    delete_ok, msg = alcohols.delete_favourite(alcohol_id)
    if not delete_ok:
        return render_template("error.html", error=msg)
    return redirect(f"/alc/{alcohol_id}")


@app.route("/grade-alc", methods=["POST"])
def grade_alcohol():
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="Toiminto ei ole sallittu.")
    alcohol_id = request.form["alcohol_id"]
    grade = request.form["grade"]
    grade_ok, msg = reviews.grade_alcohol(alcohol_id, grade)
    if not grade_ok:
        return render_template("error.html", error=msg)
    return redirect(f"alc/{alcohol_id}")


@app.route("/add-comment", methods=["POST"])
def add_comment():
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="Toiminto ei ole sallittu.")
    alcohol_id = request.form["alcohol_id"]
    sender_id = session["user_id"]
    comment = request.form["comment"]
    add_ok, msg = reviews.add_comment(alcohol_id, sender_id, comment)
    if not add_ok:
        return render_template("error.html", error=msg)
    return redirect(f"alc/{alcohol_id}")


@app.route("/delete-comment", methods=["POST"])
def delete_comment():
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="Toiminto ei ole sallittu.")
    alcohol_id = request.form["alcohol_id"]
    comment_id = request.form["comment_id"]
    delete_ok, msg = reviews.delete_comment(comment_id)
    if not delete_ok:
        return render_template("error.html", error=msg)
    return redirect(f"alc/{alcohol_id}")


@app.route("/delete-alc", methods=["POST"])
def delete_alcohol():
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="Toiminto ei ole sallittu.")
    alcohol_id = request.form["alcohol_id"]
    delete_ok, msg = alcohols.delete_alcohol(alcohol_id)
    if not delete_ok:
        return render_template("error.html", error=msg)
    reviews.delete_reviews(alcohol_id)
    return redirect("/")


@app.route("/create-user", methods=["GET", "POST"])
def create_user():
    if request.method == "GET":
        return render_template("new-user.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_2 = request.form["password_check"]
        role = request.form["role"]
        create_ok, msg = users.create_user(username, password, password_2, role)
        if not create_ok:
            return render_template("new-user.html", error=msg)
        return render_template("success.html", msg=msg)


@app.route("/profile/<int:id>")
def profile(id):
    check_ok, msg = users.is_own_profile(id)
    if not check_ok:
        return render_template("error.html", error=msg)
    own_alcohols = alcohols.list_own_alcohols(id)
    favourites = alcohols.list_favourites(id)
    return render_template("profile.html", alcohols=own_alcohols, favourites=favourites)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        check_ok, msg = users.check_login(username, password)
        if check_ok:
            return redirect("/")
        return render_template("login.html", error=msg)


@app.route("/logout")
def logout():
    try:
        users.logout()
    except:
        pass
    return redirect("/")