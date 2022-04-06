import os

from flask import render_template, flash, redirect, url_for, request
from flask import send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app, db
from app.forms import LoginForm, RegistrationForm, ImageForm
from app.models import User

from datetime import datetime


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]

    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('index'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('You\'ve successfully registered!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]

    form = ImageForm()
    return render_template('user.html', user=user, posts=posts, form=form)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = ImageForm()
    if form.validate_on_submit():
        f = form.image.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['AVATAR_UPLOAD_DIR'], filename))
        current_user.image = filename
        db.session.commit()

    return redirect(url_for('user', username=current_user.username))


@app.route('/avatars/<filename>')
@login_required
def avatars(filename):
    return send_from_directory(app.config['AVATAR_UPLOAD_DIR'], filename)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
