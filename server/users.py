"""
users.py is the part of the application which contains user validation
functions. A user can be validated via the the validate_user function.
"""
from datetime import datetime, timedelta
from server import app, users_dict, users_lock, sessions, sessions_lock
from flask import request, render_template, redirect
import bcrypt

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


def hash_password(password):
    """hash_password returns a bcrypted password_hash"""
    password = password.encode('utf-8')
    return bcrypt.hashpw(password, bcrypt.gensalt(12))


def check_password_hash(password, password_hash):
    """check_password_hash returns whether the password passed into
    the function is the corollary of the password_hash"""
    password = password.encode('utf-8')
    password_hash = password_hash.encode('utf-8')
    return bcrypt.checkpw(password, password_hash)


def get_user_by_email(email):
    """get_user_by_email will return a user dictionary or None depending
    on whether the user email exists for a user"""
    # loop over the users
    users_lock.acquire()
    for _, user in users_dict.items():
        user_email = user.get("email")
        if user_email and user_email == email:
            users_lock.release()
            return user
    users_lock.release()
    return None


def is_logged_in():
    """is_logged_in checks whether a user session exists within the system"""
    if 'session' in request.cookies:
        email, password_hash = get_session_cookie_details()
        # Check if cookie is correct according to the sessions
        for session in sessions:
            expires = datetime.strptime(session["expires"], DATETIME_FORMAT)
            now = datetime.now()
            if not email == session["email"]:
                return False
            if not password_hash == session["password_hash"]:
                return False
            if not expires > now:
                return False
            return True
    return False


def get_session_cookie_details():
    """get_session_cookie_details will return the email and password_has from the session cookie"""
    session_cookie = request.cookies["session"]
    password_hash = session_cookie[-60:]
    email = session_cookie[:len(session_cookie)-60]
    return email, password_hash


def get_user_by_session():
    """get_user_by_session wull return a user dict gathered from the session otherwise
    it will return None"""
    if 'session' in request.cookies:
        email, _ = get_session_cookie_details()
        return get_user_by_email(email)
    return None


def is_admin(user_id):
    """is_admin will return whether the user is an admin and can do the operations that
    they are trying to access"""
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
    """is_admin_redirect will check is the user is an admin, if they arnt then it will
    return an error string"""
    if not is_admin(user_id):
        return "Admin authentification required"


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
    """user_login will log the user in and create a cookie for the whole of the site.
    This method will check the authentification credentials entered by the user"""
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
        success = check_password_hash(password, password_hash)
        if not success:
            return render_template("login.html", error="Login credentials are incorrect")
        current_time = datetime.now()
        expires = current_time + timedelta(days=1) # a day
        session = {
            'email': email,
            'password_hash': password_hash,
            'expires': expires.strftime(DATETIME_FORMAT)
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
    """user_add will send a form to the user if they submit a GET request.
    This form will then send the form data back as a POST request.
    In this case the information will be taken and used for the new user."""
    if request.method == "POST":
        form = request.form
        email = form.get('email')
        if not email:
            error_string = "Error: Please enter an email"
            return render_template("new_user.html", error=error_string)
        # Check if email is already taken
        user = get_user_by_email(email)
        if user:
            return render_template("new_user.html",
                                   error="An account with that email already exists")
        password = form.get('password')
        if not password:
            error_string = "Please enter a valid password"
            return render_template("new_user.html", error=error_string)
        create_user(email, password)
        success_string = "Successfully Registered"
        return render_template("login.html", success=success_string)
    else:
        # Todo add the form template here
        return render_template("new_user.html")


@app.route("/user/delete/<int:user_id>")
def user_delete(user_id):
    """user_delete will delete the user via the /user/delete/{id} url"""
    if not is_logged_in():
        return redirect("/login")
    user = get_user_by_session()
    is_admin_redirect(user)
    deleted = delete_user(user_id)
    if deleted:
        return "User successfully deleted"
    else:
        return "User does not exist"


@app.route("/user/<int:user_id>/make_admin")
def user_make_admin(user_id):
    "user_make_admin will make a user admin"
    if not is_logged_in():
        return redirect("/login")
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
    "user_login will log a user out of the system"
    if not is_logged_in():
        return "Not logged in"
    # remove sessions
    user = get_user_by_session()
    sessions_lock.acquire()
    for session in sessions:
        if session["email"] == user["email"]:
            sessions.remove(session)
            break
    sessions_lock.release()
    return render_template("login.html", success="Successfully logged out!")


@app.route("/my_account")
def user_account():
    "user_account handles the user account details"
    if not is_logged_in():
        return redirect("/login")
    user = get_user_by_session()
    return render_template("my_account.html", user=user)