import os

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
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
    password_hash = db.Column(db.String(200), nullable=False)
    permission = db.Column(db.Integer)


    
# Register Form
class RegisterForm(FlaskForm):
    org_nr = StringField(validators=[InputRequired(), Length(min=9, max=9)], render_kw={"placeholder":"Organisation Number"})
    password = PasswordField(validators=[InputRequired(),Length(min=1, max=20), EqualTo("c_password", message="Passwords must match!")], render_kw={"placeholder":"Password"})
    c_password = PasswordField(validators=[InputRequired(),Length(min=1, max=20)], render_kw={"placeholder":"Confirm Password"})
    submit = SubmitField("Submit")

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
    org_nr = StringField(validators=[InputRequired(), Length(min=9, max=9)], render_kw={"placeholder":"Organisation Number"})
    password = PasswordField(validators=[InputRequired(),Length(min=1, max=20)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Submit")

    def validate_org_nr(form, field):
        user = User.query.filter_by(company_number=field.data).first()
        if not user:
            flash("Company not registered")
            raise ValidationError("Company not registered")
        
    def validate_password(form, field):
        user = User.query.filter_by(company_number = form.org_nr.data).first()
        if user:
            if not bcrypt.check_password_hash(user.password_hash, field.data):
                flash("Password is incorrect")
                raise ValidationError("Password is incorrect")
    



# Index Route
@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        company_name_or_code = request.form.get("company_name_or_code")
        return redirect(f"/company/{company_name_or_code}")
    else:
        return render_template("index/index.html")



# Register Page
@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        org_name = query_company(form.org_nr.data)

        user = User(company_number=form.org_nr.data,
                    company_name=org_name["info"]["org_navn"],
                    password_hash=bcrypt.generate_password_hash(form.password.data),
                    permission=0)
        db.session.add(user)
        db.session.commit()
        flash("User Created Successfully")
        return redirect(url_for("login"))

    return render_template("register/register.html", form=form)



# Login Page
@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(company_number=form.org_nr.data).first()
        login_user(user)
        return redirect(url_for("profile"))
    
    return render_template("login/login.html", form=form)


# Logout Route
@app.route("/logout", methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Entries for testing
@app.route("/entries")
def entries():
    users = User.query.all()
    results = [{"company_number":user.company_number, "company_name":user.company_name,"password":user.password_hash} for user in users]
    return render_template("/entries/entries.html",users=results)


# Profile Page
@app.route("/profile")
@login_required
def profile():
    return render_template("profile/profile.html")


# Company page for testing functionality of querycompany
@app.route("/company/<company>")
def company(company):
    company_info = query_company(company, validate_emails=False)
    if company_info == None:
        return redirect("/")
    return render_template("company/company.html", company_info=company_info)




# Run App
if __name__ == "__main__":
    app.run()