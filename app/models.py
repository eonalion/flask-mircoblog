from datetime import datetime
from hashlib import md5

from flask import url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('subscription_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    image = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', cascade="all, delete", lazy='dynamic')
    subscriptions = db.relationship('User', secondary=followers,
                                    primaryjoin=followers.c.follower_id == id,
                                    secondaryjoin=followers.c.subscription_id == id,
                                    backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def default_avatar(self):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon'

    def follow(self, user):
        if not self.is_following(user):
            self.subscriptions.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.subscriptions.remove(user)

    def is_following(self, user):
        return user in self.subscriptions

    def subscription_posts(self):
        subscription_posts = Post.query.join(
            followers, (followers.c.subscription_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own_posts = Post.query.filter_by(user_id=self.id)

        return subscription_posts.union(own_posts).order_by(Post.timestamp.desc())

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    body = db.Column(db.String(600))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.title or self.body)
