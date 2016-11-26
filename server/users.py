"""
users.py is the part of the application which contains user validation functions. A user can be validated via the the validate_user function.
"""
from server import app, users_dict
from flask import request
import bcrypt


def hash_password(password):
    """hash_password returns a bcrypted password_hash"""
    return bcrypt.hashpw(password, bcrypt.gensalt(12))


def check_password_hash(password, password_hash):
    """check_password_hash returns whether the password passed into the function is the corollary of the password_hash"""
    return bcrypt.checkpw(password, password_hash)

@app.route("/user/new", methods=["GET", "POST"])
def user_add():
    """user_add will send a form to the user if they submit a GET request. This form will then send the form data back as a POST request. In this case the information will be taken and used for the new user."""
    if request.method == "POST":

        pass
    else: 
        pass
