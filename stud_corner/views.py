from operator import pos
from flask.helpers import flash
from werkzeug.utils import redirect
from stud_corner import email
from flask import Blueprint, request, render_template, url_for
from flask_login import current_user
from flask_login.utils import login_required
from . import db
from .models import Posts


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

@views.route('/post', methods = ['GET', 'POST'])
@login_required
def post():
    if request.method == "POST":
        subject = request.form.get("subject")
        title = request.form.get("title")
        content = request.form.get("content")
        new_post = Posts(
            subject = subject,
            title=title,
            content = content,
            author = current_user
            )

        db.session.add(new_post)
        db.session.commit()

        flash("Your post is successfully created.", "success")
        return redirect(url_for("views.index"))

    return render_template("/post.html")


