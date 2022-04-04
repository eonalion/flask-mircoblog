from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=32)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=32)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')
