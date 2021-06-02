from os import environ
DEBUG = False
SQLALCHEMY_ECHO = False

####Configure Email Credential
MAIL_SERVER='smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = environ.get('MAIL_USERNAME')
MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_DEFAULT_SENDER = ("Student Corner Web", environ.get('MAIL_USERNAME'))
