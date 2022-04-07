from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=32)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=32)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=32)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=32)])
    password2 = PasswordField('Repeat Password',
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username already exists.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email address already exists.')


class ImageForm(FlaskForm):
    image = FileField('Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])

    submit = SubmitField('Save')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username already exists.')


class FollowForm(FlaskForm):
    submit = SubmitField('Submit')
