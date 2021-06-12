from operator import pos
from flask.helpers import flash
from werkzeug.utils import redirect
from stud_corner import email
from flask import Blueprint, request, render_template, url_for
from flask_login import current_user
from flask_login.utils import login_required
from . import db
from .models import Posts, User


views = Blueprint('views', __name__)


#Main page
@views.route('/')
def index():
    posts = Posts.query.order_by(Posts.date_posted.desc()).all()
    return render_template("/index.html", posts = posts)
        


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
        return redirect(url_for("views.post"))
    current_user_posts = Posts.query.filter_by(user_id = current_user.id).order_by(Posts.date_posted.desc()).all()
    return render_template("/post.html", current_user_posts = current_user_posts)

@views.route('/author/<int:id>')
def author(id):
    post = Posts.query.get_or_404(id)
    author = post.author
    author_posts = Posts.query.filter_by(user_id = author.id).order_by(Posts.date_posted.desc()).all()
    return render_template("/author.html", author = author, author_posts = author_posts)

@views.route('/read_more/<int:id>')
def read_more(id):
    post = Posts.query.get_or_404(id)
    return render_template("/read_more.html", post = post)
