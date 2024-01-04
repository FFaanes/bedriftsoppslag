import os

from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def setup():
    # APP setup
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = "-"
    app.config["HOST"] = "localhost"
    app.config["PORT"] = 5000
    app.config["DEBUG"] = True

    # Bcrypt
    bcrypt = Bcrypt(app)

    # Database Setup
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'database.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Login Management
    login_manager = LoginManager()
    login_manager.login_view = "login"

    return app, bcrypt,  login_manager