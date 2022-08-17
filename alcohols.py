from flask import session
from db import db
import photos

def get_all():
    try:
        sql = '''SELECT a.id, a.name, a.description, a.persentage, a.usage, T.name AS type,
        T.id as tagid, U.username, a.created_at, a.like_count, a.comment_count
        FROM alcohols a, users U, tags T
        WHERE a.creator_id=U.id AND T.id=a.tagid AND a.visible=1 
        GROUP BY a.id, U.id, T.id 
        ORDER BY a.created_at DESC
        LIMIT 100'''
        result = db.session.execute(sql)
        return result.fetchall()
    except:
        return False
    return True

def get_popular():
    try:
        sql = '''SELECT a.id, a.name, a.description, a.persentage, a.usage, T.name AS type,
        T.id as tagid, U.username, a.created_at,  a.like_count, a.comment_count
        FROM alcohols a, users U, tags T
        WHERE a.creator_id=U.id AND T.id=a.tagid AND a.visible=1 AND a.like_count>0
        GROUP BY a.id, U.id, T.id
        ORDER BY a.like_count DESC
        LIMIT 100'''
        result = db.session.execute(sql)
        return result.fetchall()
    except:
        return False
    return True

def get_commented():
    try:
        sql = '''SELECT a.id, a.name, a.description, a.persentage, a.usage, T.name AS type,
        T.id as tagid, U.username, a.created_at, a.like_count, a.comment_count
        FROM alcohols a, users U, tags T, comments C
        WHERE a.creator_id=U.id AND T.id=a.tagid AND a.visible=1 AND C.visible=1 AND a.comment_count>0
        GROUP BY a.id, T.id, U.id
        ORDER BY a.comment_count DESC
        LIMIT 100'''
        result = db.session.execute(sql)
        return result.fetchall()
    except:
        return False

# Getting, adding and deleting a recipe

def get(alcohol_id):
    try:
        sql = '''SELECT a.id, a.name, a.description, a.persentage, a.usage, a.creator_id,
        T.name as type, T.id as tagid, U.username, a.created_at, a.like_count, a.comment_count
        FROM alcohols a, users U, tags T
        WHERE a.id=:alcohol_id AND a.creator_id=U.id AND T.id=a.tagid AND a.visible=1'''
        result = db.session.execute(sql, {"alcohol_id":alcohol_id})
        return result.fetchone()
    except:
        return False

def add_alcohol(name, description, tagid, usage, persentage):
    creator_id = session['user_id']
    visible = 1
    try:
        sql = '''INSERT INTO alcohols (name,description,tagid,usage,persentage,
        creator_id,created_at,visible)
        VALUES (:name,:description,:tagid,:usage,:persentage,:creator_id,now(),:visible)
        RETURNING id'''
        result = db.session.execute(sql,
        {'name':name,'description':description,'tagid':tagid,
        'usage':usage,'persentage':persentage,'creator_id':creator_id,
        'visible':visible})
        db.session.commit()
        return result.fetchone()[0]
    except:
        return False


def update_alcohol(alcohol_id, name, description, tagid, usage, persentage):
    try:
        if session['admin']:
            sql = '''UPDATE alcohols SET name=:name, description=:description, usage=:usage,
            persentage=:persentage, tagid=:tagid WHERE id=:alcohol_id RETURNING id'''
            result = db.session.execute(sql,{'alcohol_id':alcohol_id, 'name':name,
            'description':description, 'usage':usage, 'persentage':persentage, 'tagid':tagid})
            db.session.commit()
            return result.fetchone()[0]
        creator_id = session['user_id']
        sql = '''UPDATE alcohols SET name=:name, description=:description, usage=:usage,
        persentage=:persentage, tagid=:tagid WHERE id=:alcohol_id AND
        creator_id=:creator_id RETURNING id'''
        result = db.session.execute(sql,{'alcohol_id':alcohol_id, 'creator_id':creator_id,
        'name':name, 'description':description, 'usage':usage, 'persentage':persentage,
        'tagid':tagid})
        db.session.commit()
        return result.fetchone()[0]
    except:
        return False

def delete_alcohol(alcohol_id):
    try:
        if session['admin']:
            sql = 'UPDATE alcohols SET visible=0 WHERE id=:alcohol_id'
            db.session.execute(sql,{'alcohol_id':alcohol_id})
            db.session.commit()
            photos.delete_photo(alcohol_id)
        else:
            creator_id = session['user_id']
            sql = 'UPDATE alcohols SET visible=0 WHERE id=:alcohol_id AND creator_id=:creator_id'
            db.session.execute(sql,{'alcohol_id':alcohol_id, 'creator_id':creator_id})
            db.session.commit()
            photos.delete_photo(alcohol_id)
    except:
        return False
    return True


def get_tags():
    try:
        sql = 'SELECT name, id FROM tags ORDER BY id'
        result = db.session.execute(sql)
        return result.fetchall()
    except:
        return False

def get_tag_name(tagid):
    try:
        sql = 'SELECT name FROM tags WHERE id=:tagid'
        result = db.session.execute(sql, {'tagid':tagid})
        return result.fetchone()
    except:
        return False


def get_profile_id(username):
    try:
        sql = 'SELECT id FROM users WHERE username=:username'
        result = db.session.execute(sql,{'username':username})
        return result.fetchone()
    except:
        return False

def get_alcohols(username):
    try:
        sql = '''SELECT a.id, a.name, a.description, T.name AS type, T.id as tagid,
        U.username, a.created_at, a.like_count, a.comment_count
        FROM alcohols a LEFT JOIN users U ON a.creator_id=U.id 
        LEFT JOIN tags T ON T.id=a.tagid
        WHERE a.visible=1 AND U.username=:username
        GROUP BY a.id, U.id, T.id 
        ORDER BY a.created_at DESC'''
        result = db.session.execute(sql,{'username':username})
        return result.fetchall()
    except:
        return False

def get_profile_likes(username):
    try:
        liker = get_profile_id(username)[0]
        sql = '''SELECT L.liker_id, a.id, a.name, a.description, T.name AS type,
        T.id as tagid, U.username, a.created_at, a.like_count, a.comment_count 
        FROM likes L JOIN alcohols a ON L.alcohol_id=a.id 
        LEFT JOIN users U ON U.id=a.creator_id
        LEFT JOIN tags T ON T.id=a.tagid 
        WHERE a.visible=1 AND L.liker_id=:liker 
        GROUP BY L.liker_id, a.id, U.id, T.id
        ORDER BY a.created_at DESC'''
        result = db.session.execute(sql, {'liker':liker})
        return result.fetchall()
    except:
        return False

def get_profile_commented(username):
    try:
        author = get_profile_id(username)[0]
        sql = '''SELECT C.author_id, a.id, a.name, a.description, T.name AS type,
        T.id as tagid, U.username, a.created_at, a.like_count, a.comment_count 
        FROM comments C JOIN alcohols a ON C.alcohol_id=a.id 
        LEFT JOIN users U ON U.id=a.creator_id
        LEFT JOIN tags T ON T.id=a.tagid 
        WHERE a.visible=1 AND C.visible=1 AND C.author_id=:author 
        GROUP BY C.author_id, a.id, U.id, T.id
        ORDER BY a.created_at DESC'''
        result = db.session.execute(sql, {'author':author})
        return result.fetchall()
    except:
        return False

def get_comments_count(alcohol_id):
    try:
        sql = 'SELECT COUNT(alcohol_id) FROM comments WHERE alcohol_id=:alcohol_id AND visible=1'
        result = db.session.execute(sql, {'alcohol_id':alcohol_id})
        return result.fetchone()
    except:
        return False

def get_comments(alcohol_id):
    try:
        sql = '''SELECT C.id, C.title, C.comment, U.username,
        C.created_at, C.author_id, C.alcohol_id
        FROM comments C, users U
        WHERE C.alcohol_id=:alcohol_id AND C.author_id=U.id AND C.visible=1
        GROUP BY C.id, U.id ORDER BY C.created_at DESC'''
        result = db.session.execute(sql, {"alcohol_id":alcohol_id})
        return result.fetchall()
    except:
        return False

def has_user_commented(alcohol_id, author_id):
    try:
        sql = 'SELECT id FROM comments WHERE alcohol_id=:alcohol_id AND author_id=:author_id'
        result = db.session.execute(sql, {'alcohol_id':alcohol_id,'author_id':author_id })
        return result.fetchone()
    except:
        return False

def add_comment(title, comment, alcohol_id):
    author_id = session['user_id']
    visible = 1
    try:
        sql = '''INSERT INTO comments(title,comment,author_id,alcohol_id,created_at,visible) VALUES
        (:title,:comment,:author_id,:alcohol_id,now(),:visible)'''
        db.session.execute(sql,{'title':title,'comment':comment,'author_id':author_id,
        'alcohol_id':alcohol_id,'visible':visible})
        db.session.commit()
    except:
        return False
    update_recipe_comment_count(alcohol_id)
    return True

def delete_comment(comment_id, alcohol_id):
    try:
        if session['admin']:
            sql = 'UPDATE comments SET visible=0 WHERE id=:comment_id'
            db.session.execute(sql,{'comment_id':comment_id})
        else:
            author_id = session['user_id']
            sql = 'UPDATE comments SET visible=0 WHERE id=:comment_id AND author_id=:author_id'
            db.session.execute(sql,{'comment_id':comment_id, 'author_id':author_id})
        db.session.commit()
    except:
        return False
    update_alcohol_comment_count(alcohol_id)
    return True

def update_alcohol_comment_count(alcohol_id):
    try:
        comment_count = get_comments_count(alcohol_id)[0]
        sql = 'UPDATE alcohols SET comment_count=:comment_count WHERE id=:alcohol_id'
        db.session.execute(sql, {'alcohol_id':alcohol_id, 'comment_count':comment_count})
        db.session.commit()
    except:
        return False
    return True

def get_like_count(alcohol_id):
    try:
        sql = 'SELECT COUNT(alcohol_id) FROM likes WHERE alcohol_id=:alcohol_id'
        result = db.session.execute(sql, {'alcohol_id':alcohol_id})
        return result.fetchone()
    except:
        return False

def has_user_liked(alcohol_id, liker_id):
    try:
        sql = 'SELECT id FROM likes WHERE alcohol_id=:alcohol_id AND liker_id=:liker_id'
        result = db.session.execute(sql, {'alcohol_id':alcohol_id,'liker_id':liker_id })
        return result.fetchone()
    except:
        return False

def like_alcohol(alcohol_id):
    liker_id = session['user_id']
    if has_user_liked(alcohol_id, liker_id):
        try:
            sql = 'DELETE FROM likes WHERE alcohol_id=:alcohol_id AND liker_id=:liker_id'
            db.session.execute(sql,{'alcohol_id':alcohol_id, 'liker_id':liker_id})
            db.session.commit()
        except:
            return False
    else:
        try:
            sql = 'INSERT INTO likes (alcohol_id, liker_id) VALUES (:alcohol_id, :liker_id)'
            db.session.execute(sql,{'alcohol_id':alcohol_id, 'liker_id':liker_id})
            db.session.commit()
        except:
            return False
    update_alcohol_like_count(alcohol_id)
    return True

def update_alcohol_like_count(alcohol_id):
    try:
        like_count = get_like_count(alcohol_id)[0]
        sql = 'UPDATE alcohols SET like_count=:like_count WHERE id=:alcohol_id'
        db.session.execute(sql, {'alcohol_id':alcohol_id , 'like_count':like_count})
        db.session.commit()
    except:
        return False
    return True

def search(searched_word):
    try:
        sql = '''SELECT a.id, a.name, a.description, T.name AS type, T.id as tagid,
        U.username, a.created_at, a.like_count, a.comment_count
        FROM alcohols a LEFT JOIN users U ON a.creator_id=U.id 
        LEFT JOIN tags T ON T.id=a.tagid
        WHERE a.name ILIKE ('%' || :searched_word || '%') 
        OR a.description ILIKE ('%' || :searched_word || '%') 
        AND a.visible=1 
        GROUP BY a.id, U.id, T.id 
        ORDER BY a.created_at DESC
        LIMIT 100'''
        result = db.session.execute(sql, {'searched_word':searched_word})
        return result.fetchall()
    except:
        return False

def search_by_tag(tagid):
    try:
        sql = '''SELECT a.id, a.name, a.description, a.persentage, a.usage,
        T.name AS type, T.id as tagid, U.username, a.created_at, a.like_count, a.comment_count
        FROM alcohols a, users U, tags T
        WHERE a.creator_id=U.id AND T.id=a.tagid AND tagid=:tagid AND a.visible=1 
        GROUP BY a.id, U.id, T.id 
        ORDER BY a.created_at DESC
        LIMIT 100'''
        result = db.session.execute(sql, { 'tagid':tagid})
        return result.fetchall()
    except:
        return False
    return True