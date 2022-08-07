from db import db


def add_tag(tag_name, alcohol_id):
    taken = alcohol_has_tag(tag_name, alcohol_id)
    if len(tag_name) and not taken:
        sql = "INSERT INTO tag (name, alcohol_id) VALUES (:tag_name, :alcohol_id)"
        db.session.execute(sql, {"tag_name":tag_name, "alcohol_id":alcohol_id})
        db.session.commit()

def alcohol_has_tag(tag_name, alcohol_id):
    sql = "SELECT * FROM tag WHERE name=:tag_name AND alcohol_id=:alcohol_id"
    result = db.session.execute(sql, {"tag_name":tag_name, "alcohol_id":alcohol_id}).fetchall()
    return bool(result)

def rename_tag(tag_name, new_name, alcohol_id):
    taken = alcohol_has_tag(new_name, alcohol_id)
    if len(new_name) and not taken:
        sql = "UPDATE tag SET name=:new_name WHERE name=:tag_name AND alcohol_id=:alcohol_id"
        db.session.execute(sql, {"new_name":new_name, "tag_name":tag_name, "alcohol_id":alcohol_id})
        db.session.commit()

def remove_tag(tag_name, alcohol_id):
    sql = "DELETE FROM tag WHERE name=:tag_name AND alcohol_id=:alcohol_id"
    db.session.execute(sql, {"tag_name":tag_name, "alcohol_id":alcohol_id})
    db.session.commit()

def tags_for_alcohol(alcohol_id):
    sql = "SELECT name FROM tag WHERE alcohol_id=:alcohol_id"
    tags = db.session.execute(sql, {"alcohol_id":alcohol_id}).fetchall()
    return tags

def tags_all():
    sql = "SELECT name FROM tag GROUP BY name"
    tags = db.session.execute(sql).fetchall()
    return tags