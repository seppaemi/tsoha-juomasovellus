from db import db

def add_alcohol(name, user_id, percentage, description):
    if active == "":
        active = 0
    if passive == "":
        passive = 0
    sql = """INSERT INTO alcohols (name, user_id, description, persentage)
            VALUES (:name, :user_id, :description, :persentage) RETURNING id"""
    recipe_id = db.session.execute(sql, {"name":name, "user_id":user_id,
                                         "instructions":description, "Percentage":float(percentage)}).fetchone()[0]
    return recipe_id

def get_all():
    sql = "SELECT id, name FROM alcohols ORDER BY name"
    return db.session.execute(sql).fetchall()

def count():
    sql = "SELECT COUNT(*) FROM alcohols"
    return db.session.execute(sql).fetchone()[0]