import os

from flask import render_template, flash, redirect, url_for, request
from flask import send_from_directory
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import app, db
from app.forms import ImageForm, EditProfileForm, EmptyForm, PostForm
from app.models import User, Post

from datetime import datetime


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    page = request.args.get('page', 1, type=int)
    posts = current_user.subscription_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))

    return render_template('index.html', title='Home', posts=posts, form=form, route='index')


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    follow_form = EmptyForm()
    delete_post_form = EmptyForm()

    return render_template('user.html', user=user, posts=posts,
                           form=follow_form, delete_form=delete_post_form,
                           route='user')


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    image_form = ImageForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile', title='Edit Profile', form=form, image_form=image_form))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile', form=form, image_form=image_form)


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

    return redirect(url_for('edit_profile'))


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    form = EmptyForm()

    if form.validate_on_submit():
        post = Post.query.filter_by(id=post_id).first()
        db.session.delete(post)
        db.session.commit()
        flash('Your post was removed')

    return redirect(url_for('user', username=current_user.username))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/explore')
@login_required
def explore():
    # posts = Post.query.order_by(Post.timestamp.desc()).all()/
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    return render_template('index.html', title='Explore', posts=posts, route='explore')


@app.route('/avatars/<filename>')
@login_required
def avatars(filename):
    return send_from_directory(app.config['AVATAR_UPLOAD_DIR'], filename)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
