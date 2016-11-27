from flask import Flask, render_template
from server import app, users_dict, polls_dict

@app.route("/")
def home():
    return render_template('index.html', polls=polls_dict, user=users_dict)

#"<h1>Data:</h1><h2>Polls:</h2><p>{0}</p><h2>Users:</h2><p>{1}</p>".format(polls_dict, users_dict)
