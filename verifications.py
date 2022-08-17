from flask import flash
import users
import alcohols

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def validate_signup(password, password2, email, username):
    if '@' not in email or users.is_email_taken(email):
        flash('Email is incorrect', 'error')
        return False
    if len(email) > 50 :
        flash('Oops! Email is too long', 'error')
        return False
    if users.is_username_taken(username):
        flash('Username is already taken.', 'error')
        return False
    if (len(password) < 9) or (len(password) > 25):
        flash('Password should be 8 to 25 characters', 'error')
        return False
    if password != password2:
        flash('Passwords do not match', 'error')
        return False
    return True

def validate_alcohol(name, description, typeid, persentage, usage):
    if len(name) > 150:
        flash('Oops! Name is too long', 'error')
        return False
    if typeid=="Choose":
        flash('Please choose the alcohol type', 'error')
        return False
    if len(description) > 1000:
        flash('Description is too long', 'error')
        return False
    if len(persentage) > 25:
        flash('Persentage too long', 'error')
        return False
    if len(usage) > 500:
        flash('Usage is too long', 'error')
        return False
    return True

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_photo(file):
    if not  allowed_file(file.filename):
        flash('Allowed image types are png, jpg, jpeg, gif', 'error')
        return False
    data = file.read()
    if len(data) > 1000*1024:
        flash('Too large a photo.', 'error')
        return False
    return True

def validate_comment(title, comment, alcohol_id):
    if len(title) > 150:
        flash('Oops! Title is too long', 'error')
        return False
    if len(comment) > 500:
        flash('Oops! Commment is too long', 'error')
        return False
    if not alcohols.get(alcohol_id):
        flash('Alcohol does not exist anymore!', 'error')
        return False
    return True