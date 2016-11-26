"""
users.py is the part of the application which contains user validation functions. A user can be validated via the the validate_user function.
"""
from server import app, users_dict, users_lock
from flask import request, render_template
import bcrypt


def hash_password(password):
    """hash_password returns a bcrypted password_hash"""
    return bcrypt.hashpw(password, bcrypt.gensalt(12))


def check_password_hash(password, password_hash):
    """check_password_hash returns whether the password passed into the function is the corollary of the password_hash"""
    return bcrypt.checkpw(password, password_hash)


def create_user(email, password):
    """create_user will add a new user to the users_dict"""
    user = {
        'email': email,
        'password_hash': hash_password(password),
        'admin': False,
        'email_verified': False,
        'strikes': 0,
        'polls': [],
        'answers': []
    }
    # Acquire lock to stop race condition
    users_lock.acquire()
    user['user_id'] = len(users_dict)
    users_dict[len(users_dict)] = user
    users_lock.release()


@app.route("/user/new", methods=["GET", "POST"])
def user_add():
    """user_add will send a form to the user if they submit a GET request. This form will then send the form data back as a POST request. In this case the information will be taken and used for the new user."""
    if request.method == "POST":
        form = request.form
        email = form.get('email')
        if not email:
            print("Incorrect user_add form, missing email.")
            error_string = "Error: Please enter an email"
            return render_template("new_user.html", error=error_string)
        password = form.get('password')
        if not password:
            print("Incorrect user_add form, missing password.")
            error_string = "Please enter a valid password"
            return render_template("new_user.html", error=error_string)
        password = password.encode('utf-8')
        email.encode('utf-8')
        create_user(email, password)
        success_string = "Successfully Added"
        return render_template("new_user.html", success=success_string)
    else: 
        # Todo add the form template here
        return render_template("new_user.html")


def delete_user(user_id):
    """delete_user will delete the user with the specified id"""
    users_lock.acquire()
    exists = users_dict.get(user_id)
    if exists:
        del users_dict[user_id]
        users_lock.release()
        return True
    else:
        users_lock.release()
        return False


@app.route("/user/delete/<int:user_id>")
def user_delete(user_id):
    """user_delete will delete the user via the /user/delete/{id} url"""
    deleted = delete_user(user_id)
    if deleted:
        return "User successfully deleted"
    else:
        return "User does not exist"
