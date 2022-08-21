from unittest import skip
from db import db
from flask import session


def list_alcohols(tag_id=None):
    if tag_id:
        try:
            sql = """SELECT A.id, A.title 
                     FROM alcohols A, 
                     alcoholtags T 
                     WHERE A.id=T.alcohol_id 
                     AND T.tag_id=:tag_id 
                     AND A.visible=1 
                     AND T.visible=1 
                     ORDER BY R.id DESC"""
            alcs = db.session.execute(sql, {"tag_id": tag_id}).fetchall()
        except:
            return []
    else:
        sql = """SELECT id, title 
                 FROM alcohols
                 WHERE visible=1
                 ORDER BY id DESC"""
    alcs = db.session.execute(sql).fetchall()
    return alcs


def list_own_alcohols(id):
    sql = """SELECT id, title 
             FROM alcohols
             WHERE creator_id=:id
             AND visible=1
             ORDER BY id DESC"""
    alcs = db.session.execute(sql, {"id": id}).fetchall()
    return alcs


def list_tags():
    sql = """SELECT id, tag 
             FROM tags"""
    tags = db.session.execute(sql).fetchall()
    return tags


def search(keyword, sortby, orderby):
    keyword = "%" + keyword.lower() + "%"
    sql = """SELECT DISTINCT A.id, A.title, A.viewed, COALESCE(AVG(G.grade), 0) AS B 
             FROM alcohols A 
             LEFT JOIN (SELECT alcohol_id, ingredient FROM ingredients WHERE visible=1) AS I
             ON A.id=I.alcohol_id 
             LEFT JOIN grades G 
             ON A.id=G.alcohol_id 
             WHERE A.visible=1 
             AND (LOWER(A.title) LIKE :keyword 
             OR LOWER(A.description) LIKE :keyword 
             OR LOWER(A.instruction) LIKE :keyword 
             OR LOWER(I.ingredient) LIKE :keyword) 
             GROUP BY A.id"""
    if sortby == "added":
        sql += " ORDER BY A.id"
    elif sortby == "grade":
        sql += " ORDER BY B"
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
    sql = """SELECT A.id, A.title 
             FROM alcohols A, favourites F 
             WHERE F.user_id=:user_id 
             AND F.alcohol_id=A.id
             AND F.visible=1
             ORDER BY F.added DESC"""
    alcs = db.session.execute(sql, {"user_id": user_id}).fetchall()
    return alcs


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
                     AND alcohol=:alcohol"""
        else:
            sql = """INSERT INTO favourites (user_id, alcohol_id, added, visible) 
                     VALUES (:user_id, :alcohol_id, NOW(), 1)"""
        db.session.execute(sql, {"user_id": user_id, "alcohol_id": alcohol_id})
        db.session.commit()
        return True, ""
    return False, "Ei löytynyt."


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
                 WHERE id=:alcohol"""
        db.session.execute(sql, {"alcohol_id": alcohol_id})
        db.session.commit()

    if alcohol_exists(alcohol_id):
        add_view()
        sql = """SELECT * 
                 FROM alcohols 
                 WHERE id=:alcohol_id"""
        alc = db.session.execute(sql, {"alcohol_id": alcohol_id}).fetchone()
        return alc, ""
    return False, "Ei löytynyt."


def get_alcohol_tags(alcohol_id):
    sql = """SELECT T.tag 
             FROM tags T, alcoholtags A 
             WHERE A.alcohol_id=:Alcohol_id 
             AND T.id=A.tag_id 
             AND R.visible=1"""
    tags = db.session.execute(sql, {"alcohol_id": alcohol_id}).fetchall()
    return tags


def get_alcohol_ingredients(alcohol_id):
    sql = """SELECT ingredient 
             FROM ingredients 
             WHERE alcohol_id=:alcohol_id
             AND visible=1"""
    ingredients = db.session.execute(sql, {"alcohol_id": alcohol_id}).fetchall()
    return ingredients


def add_alcohol(title, description, instruction, ingredients, tags):
    check_ok, msg = check_alcohol_inputs(0,
                                        title,
                                        description,
                                        instruction,
                                        ingredients)
    if not check_ok:
        return False, msg, None
    creator_id = session["user_id"]
    sql = """INSERT INTO alcohols (creator_id, created_at, viewed, title, description, instruction, visible) 
             VALUES (:creator_id, NOW(), 0, :title, :description, :instruction, 1) 
             RETURNING id"""
    alcohol_id = db.session.execute(sql, {"creator_id": creator_id, "title": title, "description": description,
                                         "instruction": instruction}).fetchone()[0]
    add_ingredients(alcohol_id, ingredients)
    add_tags(alcohol_id, tags)
    db.session.commit()
    return True, "", alcohol_id


def add_ingredients(alcohol_id, ingredients):
    for i in ingredients:
        if i != "":
            sql = """INSERT INTO ingredients (alcohol_id, ingredient, visible) 
                     VALUES (:alcohol_id, :i, 1)"""
            db.session.execute(sql, {"alcohol_id": alcohol_id, "i": i})


def add_tags(alcohol_id, tags):
    for t in tags:
        if t != "":
            sql = """INSERT INTO alcoholtags (alcohol_id, tag_id, visible) 
                     VALUES (:alcohol_id, :t, 1)"""
            db.session.execute(sql, {"alcohol_id": alcohol_id, "t": t})


def modify_alcohol(alcohol_id, title, description, instruction, ingredients, tags):
    check_ok, msg = check_alcohol_inputs(alcohol_id, title, description,
                                        instruction, ingredients)
    if not check_ok:
        return False, msg
    sql = """UPDATE alcohols 
             SET title=:title, 
             description=:description, 
             instruction=:instruction 
             WHERE id=:alcohol_id"""
    db.session.execute(sql, {"title": title, "description": description,
                       "instruction": instruction, "alcohol_id": alcohol_id})
    modify_ingredients(alcohol_id, ingredients)
    modify_tags(alcohol_id, tags)
    db.session.commit()
    return True, ""


def modify_ingredients(alcohol_id, ingredients):
    sql = """SELECT id 
             FROM ingredients 
             WHERE alcohol_id=:alcohol_id 
             AND visible=1"""
    old_ingredients = db.session.execute(
        sql, {"alcohol_id": alcohol_id}).fetchall()
    new_ingredients = [i for i in ingredients if i != ""]
    for i in range(min(len(old_ingredients), len(new_ingredients))):
        id = old_ingredients.pop(0)[0]
        ingredient = new_ingredients.pop(0)
        sql = """UPDATE ingredients 
                 SET ingredient=:ingredient 
                 WHERE id=:id"""
        db.session.execute(sql, {"ingredient": ingredient, "id": id})
    if old_ingredients:
        for i in old_ingredients:
            id = i[0]
            sql = """UPDATE ingredients 
                     SET visible=0 
                     WHERE id=:id"""
            db.session.execute(sql, {"id": id})
    else:
        for i in new_ingredients:
            sql = """INSERT INTO ingredients (alcohol_id, ingredient, visible) 
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
        own_alcohol, msg = is_own_alcohol(alcohol_id)
        if not own_alcohol:
            return False, msg
    if alcohol_exists(alcohol_id):
        sql = """UPDATE alcohols 
                 SET visible=0 
                 WHERE id=:alcohol_id"""
        db.session.execute(sql, {"alcohol_id": alcohol_id})
        sql = """UPDATE ingredients 
                 SET visible=0 
                 WHERE alcohols_id=:alcohol_id"""
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


def check_alcohol_inputs(alcohol_id, title, description, instruction, ingredients):
    if len(title) == 0:
        return False, "Nimi puuttuu."
    if len(title) > 100:
        return False, "Nimen maksimipituus on 100 merkkiä."
    if title_taken(title, alcohol_id):
        return False, "Alkoholi on jo olemassa."
    if len(description) > 2000:
        return False, "Kuvauksen maksimipituus on 2000 merkkiä."
    if len(instruction) > 2000:
        return False, "Käyttösuosituksen maksimipituus on 100 merkkiä."
    for i in ingredients:
        if len(i) > 100:
            return False, "Tuotetiedon maksimipituus on 100 merkkiä."
    return True, ""


def title_taken(title, alcohol_id):
    sql = """SELECT COUNT(*) 
             FROM alcohols 
             WHERE title=:title 
             AND visible=1 
             AND id<>:alcohol_id"""
    result = db.session.execute(
        sql, {"title": title, "alcohol_id": alcohol_id}).fetchone()[0]
    return result


def alcohol_exists(alcohol_id):
    try:
        sql = """SELECT COUNT(*) 
                FROM alcohol 
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
