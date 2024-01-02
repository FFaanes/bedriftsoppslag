import os
from datetime import date

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo

from config import app_setup
from QueryCompany.query_company import query_company


app = app_setup()
bcrypt = Bcrypt(app)

# Login Management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Setup Database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)




# User
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    company_number = db.Column(db.Integer, nullable=False, unique=True)
    company_name = db.Column(db.String(100), nullable=False)
    company_email = db.Column(db.String(50), nullable=False)
    register_date = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    permission = db.Column(db.Integer)


    
# Register Form
class RegisterForm(FlaskForm):
    email = EmailField(validators=[InputRequired()] ,render_kw={"placeholder":"E-post"})
    org_nr = StringField(validators=[InputRequired(), Length(min=9, max=9)], render_kw={"placeholder":"Org. Nummer"})
    password = PasswordField(validators=[InputRequired(),Length(min=1, max=20), EqualTo("c_password", message="Passord må være like!")], render_kw={"placeholder":"Passord"})
    c_password = PasswordField(validators=[InputRequired(),Length(min=1, max=20)], render_kw={"placeholder":"Bekreft Passord"})
    submit = SubmitField("Registrer")

    def validate_email(form, field):
        user = User.query.filter_by(company_email=field.data).first()
        if user:
            flash("Email already registered.")
            raise ValidationError("Email already registered.")

    def validate_org_nr(form, field):
        # Check if organisation number exists in database.
        user = User.query.filter_by(company_number=field.data).first()
        if user:
            flash("User already registered.")
            raise ValidationError("User already registered.")
        
        # Check if the company number exists in the register
        org_name = query_company(field.data)
        if org_name == None:
            flash("Company number not valid")
            raise ValidationError("Company number not valid")

# Login Form
class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired()], render_kw={"placeholder":"E-Post"})
    password = PasswordField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={"placeholder":"Passord"})
    submit = SubmitField("Logg Inn")

    def validate_email(form, field):
        email = str(field.data).lower()
        user = User.query.filter_by(company_email=email).first()
        if not user:
            flash("Company not registered")
            raise ValidationError("Company not registered")
        
    def validate_password(form, field):
        email = str(form.email.data).lower()
        user = User.query.filter_by(company_email=email).first()
        if user:
            if not bcrypt.check_password_hash(user.password_hash, field.data):
                flash("Password is incorrect")
                raise ValidationError("Password is incorrect")
    

class CompanySearchForm(FlaskForm):
    query = StringField(validators=[InputRequired()])
    submit = SubmitField("Søk")


# Index Route
@app.route("/", methods=["GET","POST"])
def index():
    return render_template("index/index.html")



# Register Page
@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()   
    if form.validate_on_submit():
        org_name = query_company(form.org_nr.data)

        user = User(company_number = form.org_nr.data,
                    company_name = org_name["info"]["org_navn"],
                    company_email = str(form.email.data).lower(),
                    register_date = str(date.today()),
                    password_hash = bcrypt.generate_password_hash(form.password.data),
                    permission = 0)
        db.session.add(user)
        db.session.commit()
        flash("Bruker Registrert!")
        return redirect(url_for("login"))

    return render_template("register/register.html", form=form)



# Login Page
@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = str(form.email.data).lower()
        user = User.query.filter_by(company_email=email).first()
        login_user(user)
        return redirect(url_for("profile"))
    
    return render_template("login/login.html", form=form)


# Logout Route
@app.route("/logout", methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Profile Page
@app.route("/profile")
@login_required
def profile():
    return render_template("profile/profile.html")


# Company page for testing functionality of querycompany
@app.route("/søk", methods=["GET","POST"])
@login_required
def search_page():
    form = CompanySearchForm()

    if form.validate_on_submit():
        search_query = form.query.data
        return redirect(url_for("company_search", company=search_query))
    return render_template("search_page/search_page.html", form=form)


# Company page for testing functionality of querycompany
@app.route("/bedrift/<company>")
@login_required
def company_search(company):
    company_info = query_company(company, validate_emails=False)
    if company_info == None:
        return redirect("/")
    return render_template("company/company.html", company_info=company_info)







# ------------------------ ADMIN -------------------------
@app.route("/admin")
@login_required
def admin():
    if current_user.permission != 10:
        return redirect(url_for("index"))
    users = User.query.all()

    return render_template("admin/admin.html", users=users)


class UserManagementForm(FlaskForm):
    email = StringField("Email")
    name = StringField("Name")
    permission = StringField("Permission")
    submit = SubmitField("Godta")

    verify_delete = StringField(render_kw={"placeholder":"BEKREFT"})
    delete = SubmitField("Slett Bruker")


@app.route("/admin/usermanagement/<company_number>", methods=["GET","POST"])
@login_required
def usermanagement(company_number):
    form = UserManagementForm()
    if current_user.permission != 10:
        return redirect(url_for("index"))
    
    user = User.query.filter_by(company_number=company_number).first()

    if form.validate_on_submit():
        # If Change button pressed
        if form.submit.data:
            User.query.filter_by(company_number = user.company_number).update({"company_email":str(form.email.data).lower(),
                                                                                    "company_name":form.name.data,
                                                                                    "permission":int(form.permission.data)})
            db.session.commit()
            return redirect(url_for("admin"))

        # If delete button pressed
        if form.delete.data:
            if form.verify_delete.data == "BEKREFT":
                User.query.filter_by(company_number = user.company_number).delete()
                db.session.commit()
                flash(f"{user.company_name} slettet!")
                return redirect(url_for("admin"))
            
            flash("Skriv Bekreft for å slette bruker.")
            return redirect(url_for('usermanagement', company_number=user.company_number))

    return render_template("admin/manage_user.html", user=user, form=form)


# Entries for testing
@app.route("/entries")
def entries():
    users = User.query.all()
    results = [{"company_number":user.company_number,
                 "company_name":user.company_name,
                 "email":user.company_email,
                 "register":user.register_date,
                 "permission":user.permission} for user in users]
    return render_template("/entries/entries.html",users=results)


# Creation Of Admin user.
def create_admin(username, password, user_id, email):
        user = User(company_number = user_id,
                    company_name = username,
                    company_email = email,
                    register_date = date.today(),
                    password_hash = bcrypt.generate_password_hash(password),
                    permission=10)
        db.session.add(user)
        db.session.commit()

# Run App
if __name__ == "__main__":
    app.run()