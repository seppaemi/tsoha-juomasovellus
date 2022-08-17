from flask import render_template, redirect, request, url_for, flash
from app import app
import users
import alcohols
import photos
import verifications

@app.route('/')
def index():
    latest = alcohols.get_all()
    popular = alcohols.get_popular()
    commented = alcohols.get_commented()
    types = alcohols.get_tags()
    return render_template('index.html', latest=latest, popular=popular, commented=commented,
    types=types)s

@app.route('/signup',methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        username = request.form['username']
        if not verifications.validate_signup(password, password2, email, username):
            return redirect("/signup")
        if users.signup(email, password, username):
            flash('Sign up done! Please log in', 'success')
            return render_template('login.html')
    flash('Sign up failed. Please try again later.')
    return render_template('signup.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if users.login(email, password):
            flash('You are now logged in as ' + email + '!', 'success')
            return redirect('/')
    flash('Oops! Check email and password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    users.logout()
    flash('You are now logged out!', 'success')
    return redirect('/')

@app.route('/admin', methods=['POST'])
def grant_admin_rights():
    if request.method == 'POST':
        users.check_csrf()
        username = request.form['username']
        if users.update_admin_rights(username):
            flash('You are now an admin', 'success')
            return redirect(url_for('get_profile', username=username))
    flash('Admin rights could not be given')
    return redirect(url_for('get_profile', username=username))

@app.route('/profile/<string:username>',methods=['GET'])
def get_profile(username):
    if request.method == 'GET':
        profile_alcohols = alcohols.get_alcohols(username)
        profile_likes = alcohols.get_profile_likes(username)
        profile_commented = alcohols.get_profile_commented(username)
        return render_template('profile.html', latest=profile_alcohols,
        popular=profile_likes, commented=profile_commented, username=username)
    return render_template('error.html', message='User was not found.')

@app.route('/newalcohol',methods=['GET', 'POST'])
def addalcohol():
    form = request.form
    types = alcohols.get_tags()
    if request.method == 'GET':
        return render_template('newrecipe.html', form=form, types=types)
    if request.method == 'POST':
        users.check_csrf()
        name = form['name']
        description = form['description']
        tagid = form['tagid']
        presentage = form['presentage']
        usage = form['usage']
        if not verifications.validate_alcohol(name, description, tagid, presentage, usage):
            return render_template("/newrecipe.html", form=form, types=types)
        alcohol_id = alcohols.add_recipe(name, description, tagid, presentage, usage)
        #print('onnistuuko paluu', alcohol_id)
        file = request.files["file"]
        photo_name = file.filename
        data = file.read()
        size = len(data)
        if file:
            if not verifications.validate_photo(file):
                return render_template("/newrecipe.html", form=form, types=types)
            photos.add_photo(photo_name, data, size, alcohol_id)
        return redirect(url_for('get_recipe', alcohol_id=alcohol_id))
    flash('Alcohol add failed. Please try again later.', 'error')
    return render_template("/newrecipe.html", form=form, types=types)

@app.route('/alcohol/update/<int:alcohol_id>',methods=['GET', 'POST'])
def updatealcohol(alcohol_id):
    alcohol = alcohols.get(alcohol_id)
    types = alcohols.get_tags()
    if request.method == 'GET':
        return render_template('updaterecipe.html', form=alcohol, types=types)
    if request.method == 'POST':
        users.check_csrf()
        form = request.form
        name = form['name']
        description = form['description']
        tagid = form['tagid']
        presentage = form['presentage']
        usage = form['usage']
        if not verifications.validate_alcohol(name, description, tagid, presentage, usage):
            return render_template("/updaterecipe.html", form=form, types=types)
        alcohol_id = alcohols.update_alcohol(alcohol_id, name, description, tagid, presentage, usage)
        file = request.files["file"]
        photo_name = file.filename
        data = file.read()
        size = len(data)
        if file:
            if not verifications.validate_photo(file):
                return render_template("/updaterecipe.html", form=form, types=types)
            photos.delete_photo(alcohol_id)
            photos.add_photo(photo_name, data, size, alcohol_id)
        return redirect(url_for('get_recipe', alcohol_id=alcohol_id))
    flash('You can only update your own alcohols. ')
    return render_template("/updaterecipe.html", form=form, types=types)

@app.route('/alcohol/<int:alcohol_id>',methods=['GET'])
def get_alcohol(alcohol_id):
    if request.method == 'GET':
        current_user = users.user_id()
        alcohol = alcohols.get(alcohol_id)
        all_comments = alcohols.get_comments(alcohol_id)
        comments = alcohols.get_comments_count(alcohol_id)
        liked = alcohols.has_user_liked(alcohol_id, current_user)
        photo = photos.get_photo_id(alcohol_id)
        return render_template('alcohol.html', alcohol=alcohol,
        all_comments=all_comments, comments=comments, liked=liked, photo=photo)
    return render_template('error.html', message='Alcohol was not found.')

@app.route('/alcohol/delete',methods=['POST'])
def delete_alcohol():
    alcohol_id = request.form['alcohol_id']
    if request.method == 'POST':
        users.check_csrf()
        if alcohols.delete_alcohol(alcohol_id):
            flash('Alcohol deleted successfully')
            return redirect('/')
    flash('You can delete only you own alcohols.', 'error')
    return redirect(url_for('get_alcohol', alcohol_id=alcohol_id))

@app.route('/alcohol/like',methods=['POST'])
def like_alcohol():
    if request.method == 'POST':
        users.check_csrf()
        alcohol_id = request.form['alcohol_id']
        if alcohols.like_alcohol(alcohol_id):
            flash('Like updated ', 'success')
            return redirect(url_for('get_alcohol', alcohol_id=alcohol_id))
    return render_template('error.html', message='Something went wrong')

@app.route('/newcomment',methods=['POST'])
def addcomment():
    form = request.form
    title = form['title']
    comment = form['comment']
    alcohol = form['alcohol_id']
    if request.method == 'POST':
        users.check_csrf()
        if not verifications.validate_comment(title, comment, alcohol):
            return redirect(url_for('get_alcohol', alcohol_id=alcohol))
        if alcohols.add_comment(title, comment, alcohol):
            return redirect(url_for('get_alcohol', alcohol_id=alcohol))
    flash('Comment could not be added', 'error')
    return redirect(url_for('get_alcohol', alcohol_id=alcohol))

@app.route('/alcohol/comment/delete',methods=['POST'])
def delete_comment():
    comment_id = request.form['id']
    alcohol_id = request.form['alcohol_id']
    if request.method == 'POST':
        users.check_csrf()
        if alcohols.delete_comment(comment_id, alcohol_id):
            flash('Comment deleted successfully')
            return redirect(url_for('get_alcohol', alcohol_id=alcohol_id))
    flash('You can delete only your own comments.', 'error')
    return redirect(url_for('get_alcohol', alcohol_id=alcohol_id))

@app.route('/search', methods=['GET', 'POST'])
def search():
    latest = alcohols.get_all()
    types = alcohols.get_tags()
    if request.method == 'GET':
        return render_template('search.html', alcohols=latest, types=types)
    if request.method == 'POST':
        searched_word = request.form['query']
        filtered = alcohols.search(searched_word)
        return render_template('search_result.html', alcohols=filtered,
        types=types, searched_word=searched_word)
    return render_template('search.html', alcohols=latest, types=types)

@app.route('/tag/<int:tagid>', methods=['GET'])
def search_by_tag(tagid):
    by_type = alcohols.search_by_tag(tagid)
    types = alcohols.get_tags()
    type_name = alcohols.get_tag_name(tagid)
    if request.method == 'GET':
        return render_template('type.html', alcohols=by_type, types=types,
        searched_word=type_name[0])
    return redirect('/search')

@app.route("/photo/<int:photo_id>", methods=['GET'])
def show_photo(photo_id):
    if request.method == 'GET':
        photo = photos.get_photo(photo_id)
        if photo:
            return photo
    flash('Photo does not exist.', 'error')
    return redirect('/')
    