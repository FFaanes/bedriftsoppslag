from wtforms import EmailField, StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from flask import flash
from flask_wtf import FlaskForm
from QueryCompany import query_company

from main import bcrypt
from main import User
from main import queryUserTable


# ----------------------------------------------- Register Form ----------------------------------------------------#
class RegisterForm(FlaskForm):
    email = EmailField(validators=[InputRequired()] ,render_kw={"placeholder":"E-post"})
    org_nr = StringField(validators=[InputRequired(), Length(min=9, max=9)], render_kw={"placeholder":"Org. Nummer"})
    password = PasswordField(validators=[InputRequired(),Length(min=1, max=20), EqualTo("c_password", message="Passord må være like!")], render_kw={"placeholder":"Passord"})
    c_password = PasswordField(validators=[InputRequired(),Length(min=1, max=20)], render_kw={"placeholder":"Bekreft Passord"})
    submit = SubmitField("Registrer")

    def validate_email(form, field):
        user = queryUserTable(field.data)
        if user:
            flash("Email er allerede registrert")
            raise ValidationError("Email er allerede registrert")

    def validate_org_nr(form, field):
        user = queryUserTable(field.data)
        if user:
            flash("Bruker er allerede registrert")
            raise ValidationError("Bruker er allerede registrert")
        
        # Check if the company number exists in the register
        org_name = query_company(field.data)
        if org_name == None:
            flash("Org. Nummer finnes ikke")
            raise ValidationError("Org. Nummer finnes ikke")
        



# ----------------------------------------------- Login Form ----------------------------------------------------#
class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired()], render_kw={"placeholder":"E-Post"})
    password = PasswordField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={"placeholder":"Passord"})
    submit = SubmitField("Logg Inn")

    def validate_email(form, field):
        email = str(field.data).lower()
        user = queryUserTable(field.data)
        if not user:
            flash("Bedrift er ikke registrert")
            raise ValidationError("Bedrift er ikke registrert")
        
    def validate_password(form, field):
        email = str(form.email.data).lower()
        user = queryUserTable(field.data)
        if user:
            if not bcrypt.check_password_hash(user.password_hash, field.data):
                flash("Feil passord")
                raise ValidationError("Feil passord")
            



# ----------------------------------------------- Query Company ----------------------------------------------------#
class CompanySearchForm(FlaskForm):
    query = StringField(validators=[InputRequired()], render_kw={"placeholder":"Org. Nr / Navn"})
    submit = SubmitField("Søk")




# ----------------------------------------------- Edit User Form ----------------------------------------------------#
class UserManagementForm(FlaskForm):
    email = StringField("Email")
    name = StringField("Name")
    permission = StringField("Permission")
    submit = SubmitField("Godta")

    verify_delete = StringField(render_kw={"placeholder":"BEKREFT"})
    delete = SubmitField("Slett Bruker")