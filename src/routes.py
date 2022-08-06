from app import app
from flask import render_template, request, redirect, url_for, flash, session
from services.user_service import user_service

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not user_service.login_user(username, password):
            flash(" Invalid credentials ")
            return render_template("login.html")
        return redirect("/homepage")
    return render_template("login.html")