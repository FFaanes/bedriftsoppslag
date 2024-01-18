import os
import requests
from datetime import date
import pandas as pd

from flask import render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, logout_user, current_user

from config import setup, HOST, PORT, DEBUG
from OrgOppslag import search_company
from OrgOppslag import update_brreg_files
from api_functions import api_request, api_updatedata, clear_api_cache

# ----------------------------------------------- Setup ----------------------------------------------------

# Main setup
app, bcrypt, login_manager = setup()
login_manager.init_app(app)
db = SQLAlchemy(app)

# Function to retrieve id of current user
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)



# ----------------------------------------------- Database Tables ----------------------------------------------------
# User
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    company_number = db.Column(db.Integer, nullable=False, unique=True)
    company_name = db.Column(db.String(100), nullable=False)
    company_email = db.Column(db.String(50), nullable=False)
    register_date = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    permission = db.Column(db.Integer)





# ----------------------------------------------- Index ----------------------------------------------------
@app.route("/", methods=["GET","POST"])
def index():
    return render_template("index/index.html")



# ------------------------------------------ Register Page ----------------------------------------------------
@app.route("/register", methods=["GET","POST"])
def register():
    form = f.RegisterForm()   
    if form.validate_on_submit():
        company = search_company(form.org_nr.data)
        user = User(company_number = form.org_nr.data,
                    company_name = company["brreg_info"]["org_navn"],
                    company_email = str(form.email.data).lower(),
                    register_date = str(date.today()),
                    password_hash = bcrypt.generate_password_hash(form.password.data),
                    permission = 0)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register/register.html", form=form)



# -------------------------------------------- Login Page ----------------------------------------------------
@app.route("/login", methods=["GET","POST"])
def login():
    form = f.LoginForm()
    if form.validate_on_submit():
        email = str(form.email.data).lower()
        user = User.query.filter_by(company_email=email).first()
        login_user(user)
        return redirect(url_for("profile"))
    return render_template("login/login.html", form=form)


# ------------------------------------------ Logout Route ----------------------------------------------------
@app.route("/logout", methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# -------------------------------------------- Profile Page ----------------------------------------------------
@app.route("/profile")
@login_required
def profile():
    return render_template("profile/profile.html")




# ----------------------------------------- Company Search Page ----------------------------------------------------
@app.route("/søk", methods=["GET","POST"])
@login_required
def search_page():
    form = f.CompanySearchForm()
    if form.validate_on_submit():
        search_query = form.query.data
        return redirect(url_for("company_search", company=search_query))
    return render_template("search_page/search_page.html", form=form)


# -------------------------------------------- Company Page ----------------------------------------------------
@app.route("/bedrift/<company>")
@login_required
def company_search(company):
 
    # Fetch Company info from api, will use backup solution if connection fails.
    company_info = api_request(route="/bedrift/", value=company, validate_emails=False, google_search_count=4)

    # If no company was found, returns list of closest results.
    if type(company_info) == list:
        return render_template("company/company.html",  closest_results = company_info)
    
    # If the company was found, display company page
    if type(company_info) == dict:
        return render_template("company/company.html",  company_info = company_info)
    
    # THIS IS A TEMPORARY SOLUTION
    flash("En feil har oppstått!")
    return redirect(url_for("search_page"))





# ----------------------------------------------- ADMIN ----------------------------------------------------
def admin_check():
    if current_user.permission != 10:
        return redirect(url_for("index"))



# ----------------------------------------- Admin Main Page ----------------------------------------------------
@app.route("/admin")
@login_required
def admin():
    admin_check() # Redirects if user is not admin
    users = User.query.all()
    return render_template("admin/admin.html", users=users)



# ------------------------------------- Routes to update companies from brreg ----------------------------------------------------
@app.route("/admin/updatelocaldata")
@login_required
def update_local_data():
    admin_check()
    update_brreg_files() # Update data on local server
    return redirect(url_for("admin"))



@app.route("/admin/updateapidata")
@login_required
def update_api_data():
    admin_check()
    api_updatedata() # Run Request to update brreg data on api server.
    return redirect(url_for("admin"))


@app.route("/admin/clearcache")
@login_required
def clear_cache():
    admin_check()
    clear_api_cache()
    return redirect(url_for("admin"))





# ------------------------------------- Admin User Management Page ----------------------------------------------------
@app.route("/admin/usermanagement/<company_number>", methods=["GET","POST"])
@login_required
def usermanagement(company_number):
    admin_check() # Redirects if user is not admin
    form = f.UserManagementForm()
    user = User.query.filter_by(company_number = company_number).first()

    if form.validate_on_submit():
    
        if form.submit.data:
            User.query.filter_by(company_number = user.company_number).update({"company_email":str(form.email.data).lower(), "company_name":form.name.data, "permission":int(form.permission.data)})
            db.session.commit()
            return redirect(url_for("admin"))

        if form.delete.data:
            if form.verify_delete.data == "BEKREFT":
                User.query.filter_by(company_number = user.company_number).delete()
                db.session.commit()
                flash(f"{user.company_name} slettet!")
                return redirect(url_for("admin"))
            flash("Skriv BEKREFT for å slette bruker.")
            return redirect(url_for('usermanagement', company_number=user.company_number))
    else:
        return render_template("admin/manage_user.html", user=user, form=form)






# TEMPORARY Function for creating first admin user.
def create_admin(username, password, user_id, email):
        user = User(company_number = user_id,
                    company_name = username,
                    company_email = email,
                    register_date = date.today(),
                    password_hash = bcrypt.generate_password_hash(password),
                    permission=10)
        db.session.add(user)
        db.session.commit()


import form as f
# ----------------------------------------------- Run App ----------------------------------------------------
if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)

