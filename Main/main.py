from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

from config import app_setup


app, db = app_setup()


@app.route("/")
def index():
    return "<h1>Test</h1>"



if __name__ == "__main__":
    app.run()