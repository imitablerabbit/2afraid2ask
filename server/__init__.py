"""
__init__ is the initialisation for the server, this contains the entry point start()
"""
from flask import Flask
app = Flask(__name__)

import server.users
import server.polls
import server.root
