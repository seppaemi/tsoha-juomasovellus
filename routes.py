from flask import render_template, request, redirect, session, abort
from app import app
import users
import alcohols
import userpage


@app.route("/")
def index():
    return render_template("index.html", name=users.username())

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
        if len(username) < 3 or len(username) > 25:
            error_name = "Käyttäjänimen oltava 3-25 merkin mittainen. "
        if users.is_taken(username.lower()):
            error_name = "Keksi toinen käyttäjänimi"
        if len(password1) < 7 or len(password1) > 35:
            error_length = "Salasanan oltava 8-35 merkin mittainen. "
        if error_name != "" or error_length != "" or error_match != "":
            return render_template("register.html", e_name=error_name, e_match=error_match,
                                   e_length=error_length, name=username)
        if users.register(username.lower(), password1):
            return redirect("/welcome")
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

@app.route("/favorites")
def favorites():
    return render_template("favorites.html", name=users.username(),
                           alcohol=userpage.get_favorites(users.user_id()))

@app.route("/alcoholpage")
def my_alcohols():
    return render_template("alcoholpage.html", name=users.username(),
                           alcohol=userpage.alcohol_from(users.user_id()))

@app.route("/add_new", methods=["GET", "POST"])
def add_alcohol():
    if request.method == "POST":
        if (session["csrf_token"] != request.form["csrf_token"]):
            return abort(403)
        name = request.form["name"]
        user_id = users.user_id()
        persentage = request.form["persentages"]
        description = request.form["description"]
        tag = request.form["tag"]
        # e = error
        name_e, persentage_e = "", ""
        if name == "":
            name_e = "Alkoholin nimi"
        if alcohols.is_name_taken(name):
            name_e = "Alkoholi on jo luoti"
        if persentage == "":
            persentage_e = "Anna prosenttimäärä"
        if name_e != "" or persentage_e != "":
            return render_template("add_new.html", error1=name_e, error2=persentage_e, name=name, serves=persentage,
                                   description=description, tag=tag)
        a_id = alcohols.add_alcohol(name, user_id, persentage, description, tag)
        return redirect("/alcohols/"+str(a_id))
    else:
        return render_template("add_new.html")

@app.route("/alcohols/<int:id>", methods=["GET", "POST"])
def alcohol(id):
    if request.method == "POST":
        if (session["csrf_token"] != request.form["csrf_token"]):
            return abort(403)
        data = alcohols.get_alcohol(id)
        user_id = users.user_id()
        tag_list = tag.tags_for_alcohol(id)
        for tag in tag_list:
            if tag[0] in request.form:
                alcohol = alcohols.all_with_tag(tag[0])
                heading = "Alkoholit kategoriassa "+tag[0]+":"
                return render_template("alcohol.html", list_heading=heading, alcohol=alcohol,
                                       tag=tag_list)
        if userpage.is_favorite(user_id, id):
            userpage.remove_favorite(user_id, id)
            like = "tykkää"
        else:
            userpage.add_favorite(user_id, id)
            like = "tykätty"
        favorite = alcohols.get_favorite_count(id)
        return render_template("alcohols.html", favorite_button=like, creator_id=data[2],
                               fav_count=favorite, id=str(id), name=data[1],
                               creator=users.username_recipe(data[2]), persentages=data[4],
                               description=data[3], tag=tag_list)
    elif alcohols.is_id_taken(id):
        data = alcohols.get_receipt(id)
        favorite = alcohols.get_favorite_count(id)
        tag_list = tag.tags_for_alcohol(id)
        if userpage.is_favorite(users.user_id(), id):
            like = "tykätty"
        else:
            like = "tykkää"
        return render_template("recipe.html", favorite_button=like, creator_id=data[2],
                               fav_count=favorite, id=str(id), name=data[1],
                               creator=users.username_recipe(data[2]), persentages=data[4],
                               description=data[3], tag=tag_list)
    else:
        return render_template("error.html", message="EI alkoholia!")


@app.route("/modify/<int:id>", methods=["GET", "POST"])
def modify(id):
    alc = alcohols.get_receipt(id)
    alcohol_tags = tag.tags_for_alcohol(id)
    if request.method == "POST":
        if (session["csrf_token"] != request.form["csrf_token"]):
            return abort(403)
        name_error, persentage_error, description_error= "", "", ""
        if "name" in request.form:
            name_error = alcohols.chage_name(request.form["a_name"], id)
        if "persentages" in request.form:
            persentage_error = alcohols.change_persenrage(request.form["a_serves"], id)
        if "change_description" in request.form:
            description_error = alcohols.change_instructions(request.form["description"], id)
        for tag in alcohol_tags:
            if tag[0] in request.form:
                renamed_tag = request.form["name_"+tag[0]]
                tag.rename_tag(tag[0], renamed_tag, id)
            if "remove_"+tag[0] in request.form:
                tag.remove_tag(tag[0], id)
        if "new_tag" in request.form:
            tag = request.form["add_new_tag"]
            tag.add_tag(tag, id)
            alcohol_tags = tag.tags_for_alcohol(id)
        alcohol_tags = tag.tags_for_alcohol(id)
        alc = alcohols.get_alcohol(id)
        if "ready" in request.form:
            return redirect("/recipe/"+str(id))
        return render_template("modify_alcohol.html", id=str(id), alcohol=alc,
                               tag=alcohol_tags, name_error=name_error, persentage_error=persentage_error,
                               description_error=description_error)
    else:
        return render_template("modify.html", id=str(id), alcohol=alc, tag=alcohol_tags)

@app.route("/alcohols", methods=["GET", "POST"])
def alcohols():
    if request.method == "POST":
        alcohols = alcohols.get_all()
        heading = "Kaikki alkoholit:"
        tag_list = tag.tags_all()
        if "search" in request.form:
            alc = request.form["alcohol"].lower()
            if len(alc):
                alc_id = alcohols.get_alcohol(alc)
                alcohols_cont_alc = []
                for aid in alc_id:
                    alcohols_cont_alc += alcohols.get_alcohol(aid.id)
                return render_template("alcohols.html", alcohols=alcohols_cont_alc,
                                       tag=tag_list, list_heading="Alkoholit, joiden nimessä'"
                                       + str(alc)+"':")
            if len(alc) > 0:
                return render_template("alcohols.html",
                                       error="Ei tuloksia hakusanalla '" + str(alc)+"'",
                                       list_heading="Kaikki Alkoholit:", alcohols=alcohols,
                                       tag=tag_list)
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
        return render_template("alcohols.html", list_heading=heading, alcohols=alcohols, tag=tag_list)
    if request.method == "GET":
        alcohols = alcohols.get_all()
        heading = "Kaikki alkoholit:"
        tag_list = tag.tags_all()
        return render_template("alcohols.html", list_heading=heading, alcohols=alcohols, tag=tag_list)


@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")