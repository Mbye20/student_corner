import os
import re
from os import environ
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_login import UserMixin, login_manager, login_user, LoginManager, logout_user, current_user
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

from flask_migrate import Migrate
load_dotenv()
#create flask app
def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py')
    from .views import views
    from .auth import auth
    app.register_blueprint(views, auth)


    return app
    
    
    

#Configure session timelimit

#Configure database
#### Configure postgresql database to run om server and sqlite to run on local host
app.config['SQLALCHEMY_DATABASE_URI']=environ.get('SQLITE_DATABASE_URL') or database_uri
db = SQLAlchemy(app)
migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.init_app(app)


#Create a user model

# def create_admin():
#     """Creates the admin user."""
#     db.session.add(User(
#         firstname= environ.get('FIRST_NAME'),
#         lastname= environ.get('LAST_NAME'),
#         email = environ.get('MAIL_USERNAME'),
#         password= generate_password_hash(environ.get('MAIL_PASSWORD')),
#         admin=True,
#         confirmed=True,
#         confirmed_on= datetime.now())
#     )
#     db.session.commit()
# create_admin()


#Name the serializer for the email confirmation

#Add user loader to retrieve user id from the database for user login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




if __name__ == "__main__":
    db.create_all()
    app.run(debug=False)
