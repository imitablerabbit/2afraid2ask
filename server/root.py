from flask import Flask
from server import app, users_dict, polls_dict

@app.route("/")
def home():
    return "<h1>Data:</h1><h2>Polls:</h2><p>{0}</p><h2>Users:</h2><p>{1}</p>".format(polls_dict, users_dict)
