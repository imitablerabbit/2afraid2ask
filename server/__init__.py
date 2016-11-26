"""
__init__ is the initialisation for the server, this contains the entry point start(). __init__ will also load all of the data that the server holds about the polls and the users.
"""
from os import listdir
from os.path import isfile, join
import json
from flask import Flask
app = Flask(__name__)

def get_files_in_dir(dir):
    """get_files_in_dir will return a list of the files that occur within a directory"""
    return [file for file in listdir(dir) if isfile(join(dir, file))]

def load_polls(dir="private/polls"):
    """Get polls will load up the polls from the dir. The polls will be returned from this function as a map. The map keys are the different poll ids"""
    files = get_files_in_dir(dir)
    dict = {}
    for filepath in files:
        poll = {}
        with open(join(dir, filepath)) as file:
            try:
                poll = json.load(file)
            except json.JSONDecodeError:
                print("Could not decode file {0}".format(filepath))
        id = poll.get("poll_id")
        dict[id] = poll
    return dict

def load_users(dir="private/users"):
    """load_users will load up all of the user json files in the dir."""
    files = get_files_in_dir(dir)
    dict = {}
    for filepath in files:
        user = {}
        with open(join(dir, filepath)) as file:
            try:
                user = json.load(file)
            except json.JSONDecodeError:
                print("Could not decode file {0}".format(filepath))
        id = user.get("user_id")
        dict[id] = user
    return dict

polls_dict = load_polls()
users_dict = load_users()

# Load the routes in the files below
import server.users
import server.polls
import server.root
