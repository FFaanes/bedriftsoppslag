import os

from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Config Variables
HOST = "10.0.0.11"
PORT = 5001
DEBUG = True
API_HOST = "http://127.0.0.1:5000"
API_KEY = "test_api_key"


def setup():
    # APP setup
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = "-"

    # Bcrypt
    bcrypt = Bcrypt(app)

    # Database Setup
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'database.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Login Management
    login_manager = LoginManager()
    login_manager.login_view = "login"

    return app, bcrypt, login_manager