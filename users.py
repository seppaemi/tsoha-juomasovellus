import secrets
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from db import db

def login(username, password):
    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["csrf_token"] = secrets.token_hex(16)
            return True
        else:
            return False

def user_id():
    return session.get("user_id", -1)

def is_taken(name):
    result = db.session.execute("SELECT id FROM users WHERE username=:username",
                                {"username": name})
    name = str(result.fetchone())[2:-3]
    return name

def username():
    result = db.session.execute("SELECT username FROM users WHERE id=:id", {"id": user_id()})
    name = str(result.fetchone())[2:-3]
    return name

def username_alcohols(u_id):
    result = db.session.execute("SELECT username FROM users WHERE id=:id", {"id": u_id})
    name = str(result.fetchone())[2:-3]
    return name

def logout():
    del session["user_id"]
    del session["csrf_token"]

def register(username, password):
    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username,password) VALUES (:username,:password)"
        db.session.execute(sql, {"username":username, "password":hash_value})
        db.session.commit()
        return login(username, password)
    except:
        return False