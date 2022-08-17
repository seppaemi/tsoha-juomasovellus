import os
from flask import session, request, abort
from werkzeug.security import check_password_hash, generate_password_hash
from db import db

def login(email, password):
    sql = 'SELECT id, password, username, admin FROM users WHERE email=:email'
    result = db.session.execute(sql, {'email':email})
    user = result.fetchone()
    if not user:
        return False
    if check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['email'] = email
        session['username'] = user.username
        session['admin'] = user.admin
        session["csrf_token"] = os.urandom(16).hex()
        return True
    return False

def logout():
    if user_id():
        del session['user_id']
        del session['email']
        del session['username']
        del session['admin']
        del session['csrf_token']

def signup(email, password, username):
    hash_value = generate_password_hash(password)
    try:
        sql = '''INSERT INTO users (email,password,
        username) VALUES (:email,:password,:username)'''
        db.session.execute(sql,
        {'email':email,'password':hash_value,'username':username})
        db.session.commit()
    except:
        return False
    return True

def update_admin_rights(username):
    try:
        sql = 'UPDATE users SET admin=True WHERE username=:username'
        db.session.execute(sql,{'username':username})
        db.session.commit()
    except:
        return False
    return True

def is_email_taken(email):
    sql = 'SELECT email FROM users WHERE email=:email'
    result = db.session.execute(sql, {'email':email})
    return result.fetchone()

def is_username_taken(username):
    sql = 'SELECT username FROM users WHERE username=:username'
    result = db.session.execute(sql, {'username':username})
    return result.fetchone()

def user_id():
    return session.get('user_id',0)

def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
