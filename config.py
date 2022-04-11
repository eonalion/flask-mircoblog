import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# Explicitly load .env file in case of running app without 'flask' command (automatically loads .env)
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AVATAR_UPLOAD_DIR = os.path.join(basedir, os.environ.get('UPLOAD_FOLDER') or 'uploads')
    POSTS_PER_PAGE = 6


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://', 1)