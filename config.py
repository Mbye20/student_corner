from os import environ
from dotenv import load_dotenv

load_dotenv()


class Config():
    SECRET_KEY = environ.get('SECRET_KEY')
    # REMEMBER_COOKIE_DURATION = timedelta(hours=3)
    REMEMBER_COOKIE_HTTPONLY=True
    REMEMBER_COOKIE_SECURE=True

    ####Configure Email Credential
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEFAULT_SENDER = ("Student Corner Web", environ.get('MAIL_USERNAME'))

    # Database Configurations
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    DEBUG = True

    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
        DEBUG = False
        SQLALCHEMY_ECHO = False

