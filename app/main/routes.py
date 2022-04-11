import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url

from flask import render_template, flash, redirect, url_for, request, current_app
from flask import send_from_directory
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.main import bp
from app.main.forms import ImageForm, EditProfileForm, EmptyForm, PostForm
from app.models import User, Post

from datetime import datetime


@bp.route('/')
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    page = request.args.get('page', 1, type=int)
    posts = current_user.subscription_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)

    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))

    return render_template('index.html', title='Home', posts=posts, form=form, route='main.index')


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)

    follow_form = EmptyForm()
    delete_post_form = EmptyForm()

    return render_template('user.html', user=user, posts=posts,
                           form=follow_form, delete_form=delete_post_form,
                           route='main.user')


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    image_form = ImageForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile', title='Edit Profile', form=form, image_form=image_form))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile', form=form, image_form=image_form)


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = ImageForm()

    if form.validate_on_submit():
        f = form.image.data

        upload_result = cloudinary.uploader.upload(f, folder="avatars",
                                                   quality="auto",
                                                   transformation=[
                                                       {'if': "ar_eq_1"},
                                                       {'width': 400, 'height': 400, 'crop': "fill"},
                                                       {'if': "end"},
                                                       {'if': "ar_gt_1:1"},
                                                       {'width': 400, 'height': 300, 'crop': "fill"},
                                                       {'if': "end"},
                                                       {'if': "ar_lt_1:1"},
                                                       {'width': 300, 'height': 400, 'crop': "fill"},
                                                       {'if': "end"}
                                                   ]
                                                   )

        (image_url, options) = cloudinary_url(upload_result['public_id'])
        current_user.image = image_url
        current_app.logger.info(image_url)
        db.session.commit()

    return redirect(url_for('main.edit_profile'))


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    form = EmptyForm()

    if form.validate_on_submit():
        post = Post.query.filter_by(id=post_id).first()
        db.session.delete(post)
        db.session.commit()
        flash('Your post was removed')

    return redirect(url_for('main.user', username=current_user.username))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/explore')
@login_required
def explore():
    # posts = Post.query.order_by(Post.timestamp.desc()).all()/
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)

    return render_template('index.html', title='Explore', posts=posts, route='main.explore')


# @bp.route('/avatars/<filename>')
# @login_required
# def avatars(filename):
#     return send_from_directory(current_app.config['AVATAR_UPLOAD_DIR'], filename)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
