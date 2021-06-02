from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import UserMixin, login_manager, login_user, LoginManager, logout_user, current_user
from flask_login.utils import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

views = Blueprint('views', __name__)

from . import app
from stud_corner import app

#Register mail on app
mail = Mail(app)


#Main page
@views.route('/')
def index():
    return render_template("/index.html")


@views.route('/profile')
@login_required
def profile():
    return render_template("/profile.html", firstname=current_user.firstname)

@views.route('/post')
@login_required
def post():
    return render_template(url_for("post"))


