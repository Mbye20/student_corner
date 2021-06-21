from flask import current_app
from flask_login import UserMixin
from datetime import datetime
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120))
    admin = db.Column(db.Boolean, nullable=False, default=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    posts = db.relationship('Posts', backref='author', lazy=True)

    def __repr__(self):
        return "<User(firstname='%s', lastname='%s', email='%s')>" % (self.firstname, self.lastname, self.email)



class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100))
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return "<Posts(subject='%s', title='%s')>" % (self.subject, self.title)


#To not import tables and db
@current_app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Posts=Posts)


