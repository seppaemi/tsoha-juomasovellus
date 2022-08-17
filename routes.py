from flask import render_template, redirect, request, url_for, flash
from app import app
import users
import alcohols
import photos
import validation

@app.route('/')
def index():
    latest = recipes.get_all()
    popular = recipes.get_popular()
    commented = recipes.get_commented()
    types = recipes.get_types()
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
        if not validation.validate_signup(password, password2, email, username):
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
            flash('Admin rights granted!', 'success')
            return redirect(url_for('get_profile', username=username))
    flash('Admin rights could not be given.')
    return redirect(url_for('get_profile', username=username))

# Profile page

@app.route('/profile/<string:username>',methods=['GET'])
def get_profile(username):
    if request.method == 'GET':
        profile_recipes = recipes.get_recipes(username)
        profile_likes = recipes.get_profile_likes(username)
        profile_commented = recipes.get_profile_commented(username)
        return render_template('profile.html', latest=profile_recipes,
        popular=profile_likes, commented=profile_commented, username=username)
    return render_template('error.html', message='User was not found.')

# Recipe: new recipe, recipe page, deleting recipe

@app.route('/newrecipe',methods=['GET', 'POST'])
def addrecipe():
    form = request.form
    types = recipes.get_types()
    if request.method == 'GET':
        return render_template('newrecipe.html', form=form, types=types)
    if request.method == 'POST':
        # Adding recipe details
        users.check_csrf()
        name = form['name']
        description = form['description']
        typeid = form['typeid']
        steps = form['steps']
        ingredients = form['ingredients']
        if not validation.validate_recipe(name, description, typeid, steps, ingredients):
            return render_template("/newrecipe.html", form=form, types=types)
        recipe_id = recipes.add_recipe(name, description, typeid, steps, ingredients)
        print('onnistuuko paluu', recipe_id)
        # Adding photo
        file = request.files["file"]
        photo_name = file.filename
        data = file.read()
        size = len(data)
        if file:
            if not validation.validate_photo(file):
                return render_template("/newrecipe.html", form=form, types=types)
            photos.add_photo(photo_name, data, size, recipe_id)
        return redirect(url_for('get_recipe', recipe_id=recipe_id))
    flash('Adding the recipe failed. Please try again later.', 'error')
    return render_template("/newrecipe.html", form=form, types=types)

@app.route('/recipe/update/<int:recipe_id>',methods=['GET', 'POST'])
def updaterecipe(recipe_id):
    recipe = recipes.get(recipe_id)
    types = recipes.get_types()
    if request.method == 'GET':
        return render_template('updaterecipe.html', form=recipe, types=types)
    if request.method == 'POST':
         # Adding recipe details
        users.check_csrf()
        form = request.form
        name = form['name']
        description = form['description']
        typeid = form['typeid']
        steps = form['steps']
        ingredients = form['ingredients']
        if not validation.validate_recipe(name, description, typeid, steps, ingredients):
            return render_template("/updaterecipe.html", form=form, types=types)
        recipe_id = recipes.update_recipe(recipe_id, name, description, typeid, steps, ingredients)
        # Adding photo
        file = request.files["file"]
        photo_name = file.filename
        data = file.read()
        size = len(data)
        if file:
            if not validation.validate_photo(file):
                return render_template("/updaterecipe.html", form=form, types=types)
            photos.delete_photo(recipe_id)
            photos.add_photo(photo_name, data, size, recipe_id)
        return redirect(url_for('get_recipe', recipe_id=recipe_id))
    flash('You can only update your own recipes. ')
    return render_template("/updaterecipe.html", form=form, types=types)

@app.route('/recipe/<int:recipe_id>',methods=['GET'])
def get_recipe(recipe_id):
    if request.method == 'GET':
        current_user = users.user_id()
        recipe = recipes.get(recipe_id)
        all_comments = recipes.get_comments(recipe_id)
        comments = recipes.get_comments_count(recipe_id)
        liked = recipes.has_user_liked(recipe_id, current_user)
        photo = photos.get_photo_id(recipe_id)
        return render_template('recipe.html', recipe=recipe,
        all_comments=all_comments, comments=comments, liked=liked, photo=photo)
    return render_template('error.html', message='Recipe was not found.')

@app.route('/recipe/delete',methods=['POST'])
def delete_recipe():
    recipe_id = request.form['recipe_id']
    if request.method == 'POST':
        users.check_csrf()
        if recipes.delete_recipe(recipe_id):
            flash('Done! You have now deleted the recipe.')
            return redirect('/')
    flash('You can delete only you own recipes.', 'error')
    return redirect(url_for('get_recipe', recipe_id=recipe_id))

# Recipe likes and comments

@app.route('/recipe/like',methods=['POST'])
def like_recipe():
    if request.method == 'POST':
        users.check_csrf()
        recipe_id = request.form['recipe_id']
        if recipes.like_recipe(recipe_id):
            flash('Done! Your like is now updated ', 'success')
            return redirect(url_for('get_recipe', recipe_id=recipe_id))
    return render_template('error.html', message='Something went sideways.')

@app.route('/newcomment',methods=['POST'])
def addcomment():
    form = request.form
    title = form['title']
    comment = form['comment']
    recipe = form['recipe_id']
    if request.method == 'POST':
        users.check_csrf()
        if not validation.validate_comment(title, comment, recipe):
            return redirect(url_for('get_recipe', recipe_id=recipe))
        if recipes.add_comment(title, comment, recipe):
            return redirect(url_for('get_recipe', recipe_id=recipe))
    flash('Adding comment failed. Please try again later.', 'error')
    return redirect(url_for('get_recipe', recipe_id=recipe))

@app.route('/recipe/comment/delete',methods=['POST'])
def delete_comment():
    comment_id = request.form['id']
    recipe_id = request.form['recipe_id']
    if request.method == 'POST':
        users.check_csrf()
        if recipes.delete_comment(comment_id, recipe_id):
            flash('Done! You have now deleted the comment.')
            return redirect(url_for('get_recipe', recipe_id=recipe_id))
    flash('You can delete only your own comments.', 'error')
    return redirect(url_for('get_recipe', recipe_id=recipe_id))

# Search and lists by type

@app.route('/search', methods=['GET', 'POST'])
def search():
    latest = recipes.get_all()
    types = recipes.get_types()
    if request.method == 'GET':
        return render_template('search.html', recipes=latest, types=types)
    if request.method == 'POST':
        searched_word = request.form['query']
        filtered = recipes.search(searched_word)
        return render_template('search_result.html', recipes=filtered,
        types=types, searched_word=searched_word)
    return render_template('search.html', recipes=latest, types=types)

@app.route('/type/<int:typeid>', methods=['GET'])
def search_by_type(typeid):
    by_type = recipes.search_by_type(typeid)
    types = recipes.get_types()
    type_name = recipes.get_type_name(typeid)
    if request.method == 'GET':
        return render_template('type.html', recipes=by_type, types=types,
        searched_word=type_name[0])
    return redirect('/search')

# Showing photos

@app.route("/photo/<int:photo_id>", methods=['GET'])
def show_photo(photo_id):
    if request.method == 'GET':
        photo = photos.get_photo(photo_id)
        if photo:
            return photo
    flash('Oops! Photo does not exist.', 'error')
    return redirect('/')
    