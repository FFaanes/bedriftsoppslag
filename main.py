import os
import requests
from datetime import date
import pandas as pd

from flask import render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, logout_user, current_user

from config import setup, HOST, PORT, DEBUG
from OrgOppslag import update_brreg_files
from api_functions import api_request, api_updatedata, clear_api_cache, api_historymanager, api_searchcounts

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
        user = User(company_email = str(form.email.data).lower(),
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
    # Redirects if user is not verified
    if current_user.permission < 1:
        flash("Mangler rettigheter!")
        return redirect(url_for("index"))
    
    form = f.CompanySearchForm()
    if form.validate_on_submit():
        search_query = form.query.data
        return redirect(url_for("company_search", company=search_query))
    return render_template("search_page/search_page.html", form=form)


# -------------------------------------------- Company Page ----------------------------------------------------
@app.route("/bedrift/<company>")
@login_required
def company_search(company):
 
    # Redirects if user is not verified
    if current_user.permission < 1:
        flash("Mangler rettigheter!")
        return redirect(url_for("index"))
    
    # Fetch Company info from api, will use backup solution if connection fails.
    company_info = api_request(route="/bedrift/", value=company, validate_emails=False, google_search_count=4, user=current_user.company_email)

    # If no company was found, returns list of closest results.
    if type(company_info) == list:
        return render_template("company/company.html",  closest_results = company_info)
    
    # If the company was found, display company page
    if type(company_info) == dict:
        return render_template("company/company.html",  company_info = company_info)
    
    # THIS IS A TEMPORARY SOLUTION
    flash("En feil har oppstått!")
    return redirect(url_for("search_page"))


# ----------------------------------------- Admin Main Page ----------------------------------------------------
@app.route("/admin", methods=["GET","POST"])
@login_required
def admin():
    # Redirects if user is not admin
    if current_user.permission != 10:
        flash("Mangler rettigheter!")
        return redirect(url_for("index"))
    
    # If an email was searched in the form, redirect to users page.
    email_search_form = f.AdminSearchEmail()
    if email_search_form.validate_on_submit():
        if User.query.filter_by(company_email = email_search_form.email.data).first():
            return redirect(url_for("usermanagement", company_email=email_search_form.email.data))
        else:
            flash("Fant ikke bruker!")
            return redirect(url_for("admin"))


    # Combine search counts onto the database users for display in admin page,
    # This was a simpler solution compared to reworking the database structure.
    # However that would have been the optimal solution.
    users = []
    search_counts = api_searchcounts()[1]
    for user in User.query.all():
        try:
            user_searchcount = search_counts[user.company_email]
        except KeyError:
            user_searchcount = 0

        users.append({"company_email" : user.company_email,
                      "register_date" : user.register_date,
                      "permission" : user.permission,
                      "search_count" : user_searchcount})

    # Gather search history and reverse from newest to oldest.
    search_history = dict(reversed(dict(api_historymanager("load")[1]).items()))

    return render_template("admin/admin.html", users=users, search_history=search_history, email_search_form=email_search_form)



# ------------------------------------- Routes to update companies from brreg ----------------------------------------------------
@app.route("/admin/updatelocaldata")
@login_required
def update_local_data():
    # Redirects if user is not admin
    if current_user.permission != 10:
        flash("Mangler rettigheter!")
        return redirect(url_for("index"))
    
    update_brreg_files() # Update data on local server
    return redirect(url_for("admin"))



@app.route("/admin/updateapidata")
@login_required
def update_api_data():
    # Redirects if user is not admin
    if current_user.permission != 10:
        flash("Mangler rettigheter!")
        return redirect(url_for("index"))
    
    api_updatedata() # Run Request to update brreg data on api server.
    return redirect(url_for("admin"))


@app.route("/admin/clearcache")
@login_required
def clear_cache():
    # Redirects if user is not admin
    if current_user.permission != 10:
        flash("Mangler rettigheter!")
        return redirect(url_for("index"))
    
    clear_api_cache()
    return redirect(url_for("admin"))

@app.route("/admin/clearhistory")
@login_required
def clear_history():
    if current_user.permission != 10:
            flash("Mangler rettigheter!")
            return redirect(url_for("index"))
    
    api_historymanager("remove")
    return redirect(url_for("admin"))



# ------------------------------------- Admin User Management Page ----------------------------------------------------
@app.route("/admin/usermanagement/<company_email>", methods=["GET","POST"])
@login_required
def usermanagement(company_email):
    # Redirects if user is not admin
    if current_user.permission != 10:
        flash("Mangler rettigheter!")
        return redirect(url_for("index"))
    
    form = f.UserManagementForm()
    user = User.query.filter_by(company_email = company_email).first()

    # Get users search count for view in the manage user page.
    try:
        search_count = api_searchcounts()[1][user.company_email]
    except KeyError:
        search_count = 0

    if form.validate_on_submit():    
        if form.submit.data:
            User.query.filter_by(company_email = user.company_email).update({"company_email":str(form.email.data).lower(), "permission":int(form.permission.data)})
            db.session.commit()
            return redirect(url_for("admin"))

        if form.delete.data:
            if form.verify_delete.data == "BEKREFT":
                User.query.filter_by(company_email = user.company_email).delete()
                db.session.commit()
                flash(f"{user.company_email} slettet!")
                return redirect(url_for("admin"))
            flash("Skriv BEKREFT for å slette bruker.")
            return redirect(url_for('usermanagement', company_email=user.company_email))
    else:
        return render_template("admin/manage_user.html", user=user, search_count=search_count ,form=form)






# TEMPORARY Function for creating first admin user.
def create_admin(user):
        User.query.filter_by(company_email = user.company_email).update({"permission":int(10)})
        db.session.commit()


import form as f
# ----------------------------------------------- Run App ----------------------------------------------------
if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)

