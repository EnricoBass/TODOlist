from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FieldList, RadioField, TextAreaField
from wtforms.validators import DataRequired, email_validator


class Register(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign-Up!")


class LogIn(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log-in")


class CreateList(FlaskForm):
    create_list = TextAreaField("create list", render_kw={"rows": 15, "cols": 11})
    submit = SubmitField("Create")


