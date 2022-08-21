from db import db
from flask import session


def get_comments(alcohol_id):
    sql = """SELECT U.username, C.comment, C.sent_at, C.id 
             FROM users U, comments C 
             WHERE U.id=C.sender_id 
             AND C.alcohol_id=:alcohol_id 
             AND C.visible=1 
             ORDER BY C.sent_at"""
    comments = db.session.execute(sql, {"alcohol_id": alcohol_id}).fetchall()
    return comments


def add_comment(alcohol_id, sender_id, comment):
    check_ok, msg = check_comment(comment)
    if not check_ok:
        return False, msg
    if alcohol_exists(alcohol_id):
        sql = """INSERT INTO comments (alcohol_id, sender_id, comment, sent_at, visible) 
                 VALUES (:alcohol_id, :sender_id, :comment, NOW(), 1)"""
        db.session.execute(sql, {"alcohol_id": alcohol_id,
                                 "sender_id": sender_id, "comment": comment})
        db.session.commit()
        return True, ""
    return False, "Ei löytynyt."


def delete_reviews(alcohol_id):
    sql = """UPDATE comments 
             SET visible=0 
             WHERE alcohol_id=:alcohol_id"""
    db.session.execute(sql, {"alcohol_id": alcohol_id})
    sql = """UPDATE grades 
             SET visible=0 
             WHERE alcohol_id=:alcohol_id"""
    db.session.execute(sql, {"alcohol_id": alcohol_id})
    db.session.commit()


def delete_comment(id):
    if admin() or is_own_comment(id):
        sql = """UPDATE comments 
                 SET visible=0 
                 WHERE id=:id"""
        db.session.execute(sql, {"id": id})
        db.session.commit()
        return True, ""
    return False, "Ei sallittu."


def grade_alcohol(alcohol_id, grade):
    if not check_grade(grade):
        return False, "Arvosanan on oltava kokonaisluku väliltä 1-5."
    if alcohol_exists(alcohol_id):
        sql = """INSERT INTO grades (alcohol_id, grade, visible) 
                 VALUES (:alcohol_id, :grade, 1)"""
        db.session.execute(sql, {"alcohol_id": alcohol_id, "grade": grade})
        db.session.commit()
        return True, ""
    return False, "Ei löytynyt."


def get_average(alcohol_id):
    sql = """SELECT ROUND(AVG(grade), 1) 
             FROM grades 
             WHERE alcohol_id=:alcohol_id"""
    average = db.session.execute(sql, {"alcohol_id": alcohol_id}).fetchone()[0]
    return "Ei arvosteluja" if not average else average


def check_grade(grade):
    try:
        grade = int(grade)
        if grade > 0 and grade < 6:
            return True
        return False
    except:
        return False


def alcohol_exists(alcohol_id):
    try:
        sql = """SELECT COUNT(*) 
                FROM alcohols 
                WHERE id=:alcohol_id 
                AND visible=1"""
        result = db.session.execute(sql, {"alcohol_id": alcohol_id}).fetchone()[0]
        return result
    except:
        return False


def check_comment(comment):
    if len(comment) == 0:
        return False, "Kommentti on tyhjä."
    if len(comment) > 1000:
        return False, "Kommentti on liian pitkä."
    return True, ""


def is_own_comment(comment_id):
    sql = """SELECT sender_id 
             FROM comments 
             WHERE id=:comment_id"""
    sender = db.session.execute(sql, {"comment_id": comment_id}).fetchone()
    if not sender or sender[0] != session["user_id"]:
        return False
    return True


def admin():
    try:
        return session["role"] == "admin"
    except:
        return False
