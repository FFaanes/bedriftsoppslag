from wtforms import EmailField, StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from flask import flash
from flask_wtf import FlaskForm


class RegisterForm(FlaskForm):
    email = EmailField(validators=[InputRequired()] ,render_kw={"placeholder":"E-post"})
    org_nr = StringField(validators=[InputRequired(), Length(min=9, max=9)], render_kw={"placeholder":"Org. Nummer"})
    password = PasswordField(validators=[InputRequired(),Length(min=1, max=20), EqualTo("c_password", message="Passord må være like!")], render_kw={"placeholder":"Passord"})
    c_password = PasswordField(validators=[InputRequired(),Length(min=1, max=20)], render_kw={"placeholder":"Bekreft Passord"})
    submit = SubmitField("Registrer")

    def validate_email(form, field):
        user = User.query.filter_by(company_email=field.data).first()
        if user:
            flash("Email er allerede registrert")
            raise ValidationError("Email er allerede registrert")

    def validate_org_nr(form, field):
        # Check if organisation number exists in database.
        user = User.query.filter_by(company_number=field.data).first()
        if user:
            flash("Bruker er allerede registrert")
            raise ValidationError("Bruker er allerede registrert")
        
        # Check if the company number exists in the register
        org_name = query_company(field.data)
        if org_name == None:
            flash("Org. Nummer finnes ikke")
            raise ValidationError("Org. Nummer finnes ikke")