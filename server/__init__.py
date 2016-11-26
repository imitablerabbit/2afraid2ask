"""
__init__ is the initialisation for the server, this contains the entry point start()
"""
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello(): 
    return "hello"

def start():
    Flask.run(app)
