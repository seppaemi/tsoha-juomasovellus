from db import db
from flask import session


def list_alcohols(tag_id=None):
    if tag_id:
        try:
            sql = """SELECT A.id, A.name 
                     FROM alcohols A, 
                     alcoholtags T 
                     WHERE A.id=T.alcohol_id 
                     AND T.tag_id=:tag_id 
                     AND A.visible=1 
                     AND T.visible=1 
                     ORDER BY A.id DESC"""
            alcohols = db.session.execute(sql, {"tag_id": tag_id}).fetchall()
        except:
            return []
    else:
        sql = """SELECT id, name 
                 FROM alcohols
                 WHERE visible=1
                 ORDER BY id DESC"""
        alcohols = db.session.execute(sql).fetchall()
    return alcohols


def list_own_alcohols(id):
    sql = """SELECT id, name 
             FROM alcohols 
             WHERE creator_id=:id
             AND visible=1
             ORDER BY id DESC"""
    alcohols = db.session.execute(sql, {"id": id}).fetchall()
    return alcohols


def list_tags():
    sql = """SELECT id, tag 
             FROM tags
             ORDER BY id"""
    tags = db.session.execute(sql).fetchall()
    return tags


def search(keyword, sortby, orderby):
    keyword = "%" + keyword.lower() + "%"
    sql = """SELECT DISTINCT A.id, A.name, A.viewed, COALESCE(AVG(G.grade), 0) AS A 
             FROM alcohols A 
             LEFT JOIN (SELECT alcohol_id, note FROM notes WHERE visible=1) AS N
             ON A.id=N.alcohol_id 
             LEFT JOIN grades G 
             ON A.id=G.alcohol_id 
             WHERE A.visible=1 
             AND (LOWER(A.name) LIKE :keyword 
             OR LOWER(A.description) LIKE :keyword 
             OR LOWER(A.persentage) LIKE :keyword 
             OR LOWER(N.note) LIKE :keyword) 
             GROUP BY A.id"""
    if sortby == "added":
        sql += " ORDER BY A.id"
    elif sortby == "grade":
        sql += " ORDER BY A"
    else:
        sql += " ORDER BY A.viewed"
    if orderby == "desc":
        sql += " DESC"
    results = db.session.execute(sql, {"keyword": keyword}).fetchall()
    return results


def is_favourite(alcohol_id):
    try:
        user_id = session["user_id"]
        sql = """SELECT COUNT(*) 
                 FROM favourites 
                 WHERE user_id=:user_id 
                 AND alcohol_id=:alcohol_id 
                 AND visible=1"""
        result = db.session.execute(
            sql, {"user_id": user_id, "alcohol_id": alcohol_id}).fetchone()[0]
        if result:
            return True
        return False
    except:
        return False


def list_favourites(user_id):
    sql = """SELECT A.id, A.name 
             FROM alcohols A, favourites F 
             WHERE F.user_id=:user_id 
             AND F.alcohol_id=A.id
             AND F.visible=1
             ORDER BY F.added DESC"""
    alcohols = db.session.execute(sql, {"user_id": user_id}).fetchall()
    return alcohols


def add_favourite(alcohol_id):
    def check_old_favourite():
        sql = """SELECT COUNT(*) 
                 FROM favourites 
                 WHERE user_id=:user_id 
                 AND alcohol_id=:alcohol_id 
                 AND visible=0"""
        result = db.session.execute(
            sql, {"user_id": user_id, "alcohol_id": alcohol_id}).fetchone()[0]
        return result

    if alcohol_exists(alcohol_id):
        user_id = session["user_id"]
        if check_old_favourite():
            sql = """UPDATE favourites 
                     SET visible=1, 
                     added=NOW() 
                     WHERE user_id=:user_id 
                     AND alcohol_id=:alcohol_id"""
        else:
            sql = """INSERT INTO favourites (user_id, alcohol_id, added, visible) 
                     VALUES (:user_id, :alcohol_id, NOW(), 1)"""
        db.session.execute(sql, {"user_id": user_id, "alcohol_id": alcohol_id})
        db.session.commit()
        return True, ""
    return False, "Ei löytynyt"


def delete_favourite(alcohol_id):
    if alcohol_exists(alcohol_id):
        user_id = session["user_id"]
        sql = """UPDATE favourites 
                 SET visible=0 
                 WHERE user_id=:user_id 
                 AND alcohol_id=:alcohol_id"""
        db.session.execute(sql, {"user_id": user_id, "alcohol_id": alcohol_id})
        db.session.commit()
        return True, ""
    return False, "Ei löytynyt."


def get_alcohol(alcohol_id):
    def add_view():
        sql = """UPDATE alcohols 
                 SET viewed=viewed+1 
                 WHERE id=:alcohol_id"""
        db.session.execute(sql, {"alcohol_id": alcohol_id})
        db.session.commit()

    if alcohol_exists(alcohol_id):
        add_view()
        sql = """SELECT * 
                 FROM alcohols 
                 WHERE id=:alcohol_id"""
        alcohol = db.session.execute(sql, {"alcohol_id": alcohol_id}).fetchone()
        return alcohol, ""
    return False, "Reseptiä ei löytynyt."


def get_alcohol_tags(alcohol_id):
    sql = """SELECT T.tag 
             FROM tags T, alcoholtags A 
             WHERE A.alcohol_id=:alcohol_id 
             AND T.id=A.tag_id 
             AND A.visible=1"""
    tags = db.session.execute(sql, {"alcohol_id": alcohol_id}).fetchall()
    return tags


def get_alcohol_notes(alcohol_id):
    sql = """SELECT note 
             FROM notes 
             WHERE alcohol_id=:alcohol_id 
             AND visible=1"""
    notes = db.session.execute(sql, {"alcohol_id": alcohol_id}).fetchall()
    return notes


def add_alcohol(name, description, persentage, notes, tags):
    check_ok, msg = check_alcohol_inputs(0,
                                        name,
                                        description,
                                        persentage,
                                        notes)
    if not check_ok:
        return False, msg, None
    creator_id = session["user_id"]
    sql = """INSERT INTO alcohols (creator_id, created_at, viewed, name, description, persentage, visible) 
             VALUES (:creator_id, NOW(), 0, :name, :description, :persentage, 1) 
             RETURNING id"""
    alcohol_id = db.session.execute(sql, {"creator_id": creator_id, "name": name, "description": description,
                                         "persentage": persentage}).fetchone()[0]
    add_notes(alcohol_id, notes)
    add_tags(alcohol_id, tags)
    db.session.commit()
    return True, "", alcohol_id


def add_notes(alcohol_id, notes):
    for i in notes:
        if i != "":
            sql = """INSERT INTO notes (alcohol_id, note, visible) 
                     VALUES (:alcohol_id, :i, 1)"""
            db.session.execute(sql, {"alcohol_id": alcohol_id, "i": i})


def add_tags(alcohol_id, tags):
    for t in tags:
        if t != "":
            sql = """INSERT INTO alcoholtags (alcohol_id, tag_id, visible) 
                     VALUES (:alcohol_id, :t, 1)"""
            db.session.execute(sql, {"alcohol_id": alcohol_id, "t": t})


def modify_alcohols(alcohol_id, name, description, persentage, notes, tags):
    check_ok, msg = check_alcohol_inputs(alcohol_id, name, description,
                                        persentage, notes)
    if not check_ok:
        return False, msg
    sql = """UPDATE alcohols 
             SET name=:name, 
             description=:description, 
             persentage=:persentage 
             WHERE id=:alcohol_id"""
    db.session.execute(sql, {"name": name, "description": description,
                       "persentage": persentage, "alcohol_id": alcohol_id})
    modify_notes(alcohol_id, notes)
    modify_tags(alcohol_id, tags)
    db.session.commit()
    return True, ""


def modify_notes(alcohol_id, notes):
    sql = """SELECT id 
             FROM notes 
             WHERE alcohol_id=:alcohol_id 
             AND visible=1"""
    old_notes = db.session.execute(
        sql, {"alcohol_id": alcohol_id}).fetchall()
    new_notes = [i for i in notes if i != ""]
    for i in range(min(len(old_notes), len(new_notes))):
        id = old_notes.pop(0)[0]
        note = new_notes.pop(0)
        sql = """UPDATE notes 
                 SET note=:note 
                 WHERE id=:id"""
        db.session.execute(sql, {"note": note, "id": id})
    if old_notes:
        for i in old_notes:
            id = i[0]
            sql = """UPDATE notes 
                     SET visible=0 
                     WHERE id=:id"""
            db.session.execute(sql, {"id": id})
    else:
        for i in new_notes:
            sql = """INSERT INTO notes (alcohol_id, note, visible) 
                     VALUES (:alcohol_id, :i, 1)"""
            db.session.execute(sql, {"alcohol_id": alcohol_id, "i": i})


def modify_tags(alcohol_id, tags):
    sql = """SELECT tag_id, visible 
             FROM alcoholtags 
             WHERE alcohol_id=:alcohol_id"""
    result = db.session.execute(sql, {"alcohol_id": alcohol_id}).fetchall()
    old_tags = [t[0] for t in result if t[1] == 1]
    removed_tags = [t[0] for t in result if t[1] == 0]
    new_tags = [int(t) for t in tags if t != ""]
    for t in new_tags:
        if t in removed_tags:
            sql = """UPDATE alcoholtags 
                     SET visible=1 
                     WHERE alcohol_id=:alcohol_id 
                     AND tag_id=:t"""
            db.session.execute(sql, {"alcohol_id": alcohol_id, "t": t})
        elif t not in old_tags[:]:
            sql = """INSERT INTO alcoholtags (alcohol_id, tag_id, visible) 
                     VALUES (:alcohol_id, :t, 1)"""
            db.session.execute(sql, {"alcohol_id": alcohol_id, "t": t})
        else:
            old_tags.remove(t)
    if old_tags:
        for t in old_tags:
            sql = """UPDATE alcoholtags 
                     SET visible=0 
                     WHERE alcohol_id=:alcohol_id 
                     AND tag_id=:t"""
            db.session.execute(sql, {"alcohol_id": alcohol_id, "t": t})


def delete_alcohol(alcohol_id):
    if not admin():
        own_alc, msg = is_own_alcohol(alcohol_id)
        if not own_alc:
            return False, msg
    if alcohol_exists(alcohol_id):
        sql = """UPDATE alcohols 
                 SET visible=0 
                 WHERE id=:alcohol_id"""
        db.session.execute(sql, {"alcohol_id": alcohol_id})
        sql = """UPDATE notes 
                 SET visible=0 
                 WHERE alcohol_id=:alcohol_id"""
        db.session.execute(sql, {"alcohol_id": alcohol_id})
        sql = """UPDATE alcoholtags 
                 SET visible=0 
                 WHERE alcohol_id=:alcohol_id"""
        db.session.execute(sql, {"alcohol_id": alcohol_id})
        sql = """UPDATE favourites 
                 SET visible=0 
                 WHERE alcohol_id=:alcohol_id"""
        db.session.execute(sql, {"alcohol_id": alcohol_id})
        db.session.commit()
        return True, ""
    return False, "Ei löytynyt"


def check_alcohol_inputs(alcohol_id, name, description, persentage, notes):
    if len(name) == 0:
        return False, "Nimi puuttuu"
    if len(name) > 1000:
        return False, "Nimi voi olla maksimissaan 100 merkkiä"
    if name_taken(name, alcohol_id):
        return False, "Alkoholi on jo luotu"
    if len(description) > 2000:
        return False, "Kuvauksen maksimipituus on 2000 merkkiä."
    if len(persentage) > 8:
        return False, "prosentti liian suuri"
    for i in notes:
        if len(i) > 100:
            return False, "Vivahteen maksimipituus on 100 merkkiä"
    return True, ""


def name_taken(name, alcohol_id):
    sql = """SELECT COUNT(*) 
             FROM alcohols 
             WHERE name=:name 
             AND visible=1 
             AND id<>:alcohol_id"""
    result = db.session.execute(
        sql, {"name": name, "alcohol_id": alcohol_id}).fetchone()[0]
    return result


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


def is_own_alcohol(alcohol_id):
    sql = """SELECT creator_id 
             FROM alcohols 
             WHERE id=:alcohol_id"""
    creator = db.session.execute(sql, {"alcohol_id": alcohol_id}).fetchone()
    try:
        if not creator or creator[0] != session["user_id"]:
            return False, "Toiminto ei ole sallittu."
        return True, ""
    except:
        return False, "Toiminto ei ole sallittu."


def admin():
    try:
        return session["role"] == "admin"
    except:
        return False