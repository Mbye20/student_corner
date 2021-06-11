from flask.helpers import flash
from werkzeug.utils import redirect
from stud_corner import email
from flask import Blueprint, request, render_template, url_for
from flask_login import current_user
from flask_login.utils import login_required
from . import db

views = Blueprint('views', __name__)


#Main page
@views.route('/')
def index():
    return render_template("/index.html")


@views.route('/profile', methods = ['GET', 'POST'])
@login_required
def profile():
    if request.method == "POST":
        email = request.form.get("email")
        bio = request.form.get("bio")
        current_user.email = email
        current_user.bio = bio
        db.session.commit()

        flash("Your Profile is Updated Succesfully!", "success")
        return redirect(url_for("views.profile"))
    return render_template(
        "/profile.html",
        firstname=current_user.firstname,
        lastname = current_user.lastname,
        email = current_user.email,
        bio = current_user.bio
        )

@views.route('/post')
@login_required
def post():
    return render_template("/post.html")


