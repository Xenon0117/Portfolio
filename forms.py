from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# TODO: Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    name=StringField("Username:",validators=[DataRequired(message="John Doe")])
    email=StringField("Email:", validators=[DataRequired(message="example@example.com")])
    password=PasswordField("Password:",validators=[DataRequired(message="Enter Your password")])
    submit=SubmitField("Register")

# TODO: Create a LoginForm to login existing users
class LogInForm(FlaskForm):
    email=StringField("Email:", validators=[DataRequired(message="example@example.com")])
    password=PasswordField("Password:",validators=[DataRequired(message="Enter Your password")])
    submit=SubmitField("Log In")


