from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy

from config import app_setup
from QueryCompany.query_company import query_company


app, db = app_setup()


@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        company_name_or_code = request.form.get("company_name_or_code")
        return redirect(f"/company/{company_name_or_code}")
    else:
        return render_template("index/index.html")

@app.route("/company/<company>")
def company(company):
    company_info = query_company(company, validate_emails=False)
    return render_template("company/company.html", company_info=company_info)


if __name__ == "__main__":
    app.run()