"""
users.py is the part of the application which contains user validation functions. A user can be validated via the the validate_user function.
"""
from server import app, users_dict, users_lock, sessions, sessions_lock
from flask import request, render_template, redirect, Response, make_response
import bcrypt
from datetime import datetime, timedelta


def hash_password(password):
    """hash_password returns a bcrypted password_hash"""
    password = password.encode('utf-8')
    return bcrypt.hashpw(password, bcrypt.gensalt(12))


def check_password_hash(password, password_hash):
    """check_password_hash returns whether the password passed into the function is the corollary of the password_hash"""
    password = password.encode('utf-8')
    password_hash = password_hash.encode('utf-8')
    return bcrypt.checkpw(password, password_hash)


def get_user_by_email(email):
    # loop over the users
    users_lock.acquire()
    for key, user in users_dict.items():
        if user["email"] == email:
            users_lock.release()
            return user
    users_lock.release()
    return None


def is_logged_in():
    if 'session' in request.cookies:
        email, password_hash = get_session_cookie_details(request.cookies["session"])
        print(email)
        print(password_hash)
        # Check if cookie is correct according to the sessions
        for session in sessions:
            if email == session["email"] and password_hash == session["password_hash"] and expires > datetime.now():
                return True
    return False


def is_logged_in_redirect(fn):
    if not is_logged_in():
        redirect("/login")


def get_session_cookie_details(cookie):
    session_cookie = request.cookies["session"]
    password_hash = session_cookie[:-60]
    email = session_cookie[:len(session_cookie)-60]
    return email, password_hash


def get_user_by_session():
    if 'session' in request.cookies:
        email, password_hash = get_session_cookie_details(request.cookies["session"])
        return get_user_by_email(email)


def is_admin(user_id):
    """is_admin will return whether the user is an admin and can do the operations that they are trying to access"""
    users_lock.acquire()
    user = users_dict.get(user_id)
    if user:
        admin = user['admin']
        if admin:
            users_lock.release()
            return True    
    users_lock.release()
    return False


def is_admin_redirect(user_id):
    if not is_admin(user_id):
        return "404 page not found"


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
    users_lock.acquire()
    user['user_id'] = len(users_dict)
    users_dict[len(users_dict)] = user
    users_lock.release()


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


# Routing takes place from here onwards
@app.route("/login", methods=["GET", "POST"])
def user_login():
    """user_login will log the user in and create a cookie for the whole of the site. This method will check the authentification credentials entered by the user"""
    if request.method == "POST":
        form = request.form
        email = form.get("email")
        if not email:
            return render_template("login.html", error="Invalid email address") 
        password = form.get("password")
        if not password:
            return render_template("login.html", error="Incorrect password")
        user = get_user_by_email(email)
        if not user:
            return render_template("login.html", error="Email address not found")
        password_hash = user["password_hash"].decode('utf-8')
        print(password_hash)
        success = check_password_hash(password, password_hash)
        if not success:
            return render_template("login.html", error="Login credentials are incorrect")
        current_time = datetime.now()
        expires = current_time + timedelta(days=1) # a day
        session = {
            'email': email,
            'password_hash': password_hash,
            'expires': expires 
        }
        # remove previous sessions for that email
        sessions_lock.acquire()
        sessions.append(session)
        sessions_lock.release()
        session_value = email + password_hash
        resp = redirect("/")
        resp.set_cookie("session", value=session_value, expires=expires)
        return resp
    else:
        return render_template("login.html") 


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
        # Check if email is already taken
        user = get_user_by_email(email)
        if user:
            print("Attempted duplicate user creation")
            return render_template("new_user.html", error="An account with that email already exists")
        password = form.get('password')
        if not password:
            print("Incorrect user_add form, missing password.")
            error_string = "Please enter a valid password"
            return render_template("new_user.html", error=error_string)
        create_user(email, password)
        success_string = "Successfully Added"
        return render_template("new_user.html", success=success_string)
    else: 
        # Todo add the form template here
        return render_template("new_user.html")


@app.route("/user/delete/<int:user_id>")
def user_delete(user_id):
    """user_delete will delete the user via the /user/delete/{id} url"""
    is_logged_in_redirect()
    is_admin_redirect()
    deleted = delete_user(user_id)
    if deleted:
        return "User successfully deleted"
    else:
        return "User does not exist"


@app.route("/user/<int:user_id>/make_admin")
def user_make_admin(user_id):
    is_logged_in_redirect()
    if not is_admin(get_user_by_session()):
        return "404 page not found"
    user_login.acquire()
    user = users_dict.get(user_id)
    if not user:
        users_lock.release()
        return "User not found"
    user["admin"] = True
    users_lock.release()
    return "User successfully updated to admin"


@app.route("/logout")
def user_logout():
    if not is_logged_in():
        return "Not logged in"
    # remove sessions
    user = get_user_by_session()
    sessions_lock.acquire()
    for session in sessions:
        if session["email"] == user["email"]:
            sessions.remove(session)
            break
    return "Logged out"

        
