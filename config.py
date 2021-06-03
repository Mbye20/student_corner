from os import environ
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    SQLALCHEMY_ECHO = False

    REMEMBER_COOKIE_DURATION = timedelta(days=1)
    
    ####Configure Email Credential
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEFAULT_SENDER = ("Student Corner Web", environ.get('MAIL_USERNAME'))
