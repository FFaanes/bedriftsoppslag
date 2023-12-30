from flask import Flask


def app_setup():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = "-"
    app.config["HOST"] = "localhost"
    app.config["PORT"] = 5000
    app.config["DEBUG"] = False
    return app