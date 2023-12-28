from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def app_setup():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = "-"
    app.config["HOST"] = "localhost"
    app.config["PORT"] = 5000
    app.config["DEBUG"] = False

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
    db = SQLAlchemy(app)

    return app, db