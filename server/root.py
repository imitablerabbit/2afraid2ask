from flask import Flask, Blueprint
from server import app

@app.route("/")
def hello(): 
    return "hello"
