from stud_corner import email
from flask import Blueprint, request, render_template, url_for
from flask_login import current_user
from flask_login.utils import login_required

views = Blueprint('views', __name__)


#Main page
@views.route('/')
def index():
    return render_template("/index.html")


@views.route('/profile')
@login_required
def profile():
    return render_template(
        "/profile.html",
        firstname=current_user.firstname,
        lastname = current_user.lastname,
        email = current_user.email
        )

@views.route('/post')
@login_required
def post():
    return render_template("/post.html")


