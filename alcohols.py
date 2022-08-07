from db import db

def add_alcohol(name, user_id, percentage, description):
    if active == "":
        active = 0
    if passive == "":
        passive = 0
    sql = """INSERT INTO alcohols (name, user_id, description, persentage)
            VALUES (:name, :user_id, :description, :persentage) RETURNING id"""
    alcohol_id = db.session.execute(sql, {"name":name, "user_id":user_id,
                                         "instructions":description, "Percentage":float(percentage)}).fetchone()[0]
    return alcohol_id

def get_all():
    sql = "SELECT id, name FROM alcohols ORDER BY name"
    return db.session.execute(sql).fetchall()

def count():
    sql = "SELECT COUNT(*) FROM alcohols"
    return db.session.execute(sql).fetchone()[0]

def get_alcohol(a_id):
    sql = "SELECT * FROM alcohols WHERE id=:id"
    res = db.session.execute(sql, {"id": a_id}).fetchall()
    return res[0]

def is_id_taken(a_id):
    sql = "SELECT id FROM alcohols WHERE id=:id"
    res = db.session.execute(sql, {"id": a_id}).fetchall()
    return bool(res)

def is_name_taken(a_name):
    sql = "SELECT id FROM alcohols WHERE name=:name"
    res = db.session.execute(sql, {"name": a_name}).fetchall()
    return bool(res)

def get_name(a_id):
    sql = "SELECT name FROM alcohols WHERE id=:id"
    return db.session.execute(sql, {"id": a_id}).fetchone()[0]

def get_favorite_count(a_id):
    sql = """SELECT COUNT(a.id) FROM alcohols as a JOIN favorites as f ON a.id=f.alcohol_id
            WHERE a.id=:id"""
    return db.session.execute(sql, {"id": a_id}).fetchone()[0]

def update_average_rating(alcohol_id):
    sql = """SELECT AVG(rating) FROM review WHERE alcohol_id=:alcohol_id"""
    result = db.session.execute(sql, {"alcohol_id": alcohol_id})
    average_rating = result.fetchone()[0]

    if average_rating == None:
        average_rating = 0
    else:
        average_rating = round(average_rating, 1)

    sql = """UPDATE alcohols SET average_rating=:average_rating WHERE id=:alcohol_id"""
    db.session.execute(
        sql, {"average_rating": average_rating, "alcohol_id": alcohol_id}
    )
    db.session.commit()

# different alcohols sortings
def all_with_tag(tag_name):
    sql = """SELECT a.id, a.name FROM alcohols as a, tag as t
            WHERE t.alcohol_id=a.id AND t.name=:tag_name"""
    return db.session.execute(sql, {"tag_name":tag_name}).fetchall()

# different alcohols orders
def all_order_novelty():
    sql = "SELECT id, name FROM alcohols ORDER BY id DESC"
    return db.session.execute(sql).fetchall()

def all_order_by_favorite():
    sql = """SELECT a.id, a.name FROM alcohols as a LEFT JOIN favorites as f
    ON a.id = f.alcohol_id GROUP BY a.id ORDER BY COUNT(f.alcohol_id) DESC"""
    return db.session.execute(sql).fetchall()

def all_order_by_persentage():
    sql = """SELECT id, name FROM alcohols ORDER BY persentage DESC"""
    return db.session.execute(sql).fetchall()

# change alcohol info
def chage_name(new_name, alcohol_id):
    taken = is_name_taken(new_name)
    if not taken:
        sql = "UPDATE alcohols SET name=:new_name WHERE id=:alcohol_id"
        db.session.execute(sql, {"new_name":new_name, "alochol_id":alcohol_id})
        db.session.commit()
        return ""
    if new_name == get_name(alcohol_id):
        return ""
    return "Alhoholi '"+new_name+"' on jo luotu"

def change_servings(new_persentage, alcohol_id):
    if int(new_persentage) < 1:
        return "Annoksia on oltava vähintään 1"
    sql = "UPDATE alcohols SET serves=:serves WHERE id=:alcohol_id"
    db.session.execute(sql, {"serves":new_persentage, "alcohol_id":alcohol_id})
    db.session.commit()
    return ""

def change_instructions(new_description, alcohol_id):
    if len(new_description):
        sql = "UPDATE alcohols SET description=:description WHERE id=:alcohol_id"
        db.session.execute(sql, {"description":new_description, "alcohol_id":alcohol_id})
        db.session.commit()
        return ""
    return "Lisää kuvaus"