from db import db

def add_favorite(user_id, alcohol_id):
    sql = "INSERT INTO favorites (user_id, alcohol_id) VALUES (:user_id, :alcohol_id)"
    db.session.execute(sql, {"user_id":user_id, "alcohol_id":alcohol_id})
    db.session.commit()

def get_favorites(user_id):
    sql = """SELECT a.id, a.name FROM favorites as f, alcohol as a
          WHERE f.alcohol_id = a.id AND f.user_id=:user_id"""
    return db.session.execute(sql, {"user_id": user_id}).fetchall()

def is_favorite(user_id, alcohol_id):
    sql = "SELECT * FROM favorites WHERE user_id=:user_id AND alcohol_id=:alcohol_id"
    result = db.session.execute(sql, {"user_id": user_id, "alcohol_id": alcohol_id}).fetchall()
    return bool(result)

def remove_favorite(user_id, alcohol_id):
    sql = "DELETE FROM favorites WHERE user_id=:user_id AND alcohol_id=:alcohol_id"
    db.session.execute(sql, {"user_id": user_id, "alcohol_id": alcohol_id})
    db.session.commit()

def alcohol_from(user_id):
    sql = "SELECT id, name FROM alcohol WHERE user_id=:user_id"
    return db.session.execute(sql, {"user_id": user_id}).fetchall()