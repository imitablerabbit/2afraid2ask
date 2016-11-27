"""
__init__ is the initialisation for the server, this contains the entry point start(). __init__ will also load all of the data that the server holds about the polls and the users.
"""
from os import listdir
from os.path import isfile, join
import json
import threading
import jinja2
from flask import Flask
app = Flask(__name__)


def get_files_in_dir(dir):
    """get_files_in_dir will return a list of the files that occur within a directory"""
    return [file for file in listdir(dir) if isfile(join(dir, file))]


def load_polls(dir="private/polls"):
    """Get polls will load up the polls from the dir. The polls will be returned from this function as a map. The map keys are the different poll ids"""
    files = get_files_in_dir(dir)
    dict = {}
    for filename in files:
        poll = {}
        filepath = join(dir, filename)
        with open(filepath) as file:
            try:
                poll = json.load(file)
            except json.JSONDecodeError:
                print("Could not decode file {0}".format(filepath))
            except UnicodeDecodeError:
                print("Could not decode unicode in {0}".format(filepath))
        id = poll.get("poll_id")
        dict[id] = poll
    return dict


def load_users(dir="private/users"):
    """load_users will load up all of the user json files in the dir."""
    files = get_files_in_dir(dir)
    dict = {}
    for filename in files:
        user = {}
        filepath = join(dir, filename)
        with open(filepath) as file:
            try:
                user = json.load(file)
            except json.JSONDecodeError:
                print("Could not decode file {0}".format(filepath))
            except UnicodeDecodeError:
                print("Could not decode unicode in {0}".format(filepath))
        id = user.get("user_id")
        dict[id] = user
    return dict


def load_sessions(filepath="private/sessions.json"):
    sessions = []
    with open(filepath) as file:
        try:
            sessions = json.load(file)
        except json.JSONDecodeError:
            print("Could not decode file {0}".format(filepath))
        except UnicodeDecodeError:
            print("Could not decode unicode in {0}".format(filepath))
    return sessions


# Load the data from the files
polls_dict = load_polls()
users_dict = load_users()
polls_lock = threading.Lock()
users_lock = threading.Lock()
sessions = load_sessions()
sessions_lock = threading.Lock()

# Load the templating files from a different directory
my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader("private/templates")
])
app.jinja_loader = my_loader

# Load the routes in the files below
import server.users
import server.polls
import server.root
