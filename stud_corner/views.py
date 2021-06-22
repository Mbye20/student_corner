from re import search
from flask import abort
from flask import Blueprint, request, render_template, url_for, flash, redirect
from flask_login import current_user
from flask_login.utils import login_required
from sqlalchemy import or_
from sqlalchemy.orm import query
from . import db
from .models import Posts, User


views = Blueprint('views', __name__)


#Main page
@views.route('/')
def index():
    page = request.args.get("page", 1, int)
    to_search = request.args.get("search")
    if to_search:
        to_search = to_search.strip()
        pag_posts = (Posts.query.join(User)
        .filter(or_(Posts.title.ilike(f'%{to_search}%'),
        Posts.subject.ilike(f'%{to_search}%'),
        Posts.content.ilike(f'%{to_search}%'),
        User.firstname.ilike(f'%{to_search}%'),
        User.lastname.ilike(f'%{to_search}%'),
        User.firstname.startswith(to_search[:3]),
        User.lastname.endswith(to_search[-3:])
        )).order_by(Posts.date_posted.desc())
        .paginate(page = page, per_page = 5))
        if pag_posts.total == 0:
            flash("Nothing related to your search was found.", "warning")
            return redirect(url_for("views.index"))
    else:
        pag_posts = (Posts.query.order_by(Posts.date_posted
        .desc()).paginate(page = page, per_page = 5))
    return render_template("/index.html", pag_posts = pag_posts)
        


@views.route('/profile', methods = ['GET', 'POST'])
@login_required
def profile():
    if request.method == "POST":
        email = request.form.get("email")
        bio = request.form.get("bio")
        user = User.query.filter_by(email=email).first()
        if user and user != current_user:
            flash("An account has already been created with this email address.", "warning")
            return redirect(url_for("views.profile"))
        elif bio != current_user.bio and email == current_user.email:
            current_user.bio = bio
            db.session.commit()
            flash("Your Bio is Updated Succesfully!", "success")
            return redirect(url_for("views.profile"))            

        elif email != current_user.email and bio == current_user.bio:
            current_user.email = email
            db.session.commit()
            flash("Your Email is Updated Succesfully!", "success")
            return redirect(url_for("views.profile"))

        elif email != current_user.email and bio != current_user.bio:          
            current_user.email = email
            current_user.bio = bio
            db.session.commit()

            flash("Your Profile is Updated Succesfully!", "success")
            return redirect(url_for("views.profile"))
        else:
            flash("No change have been made on your profile!", "warning")
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
    page = request.args.get("page", 1, int)
    to_search = request.args.get("search")
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
    if to_search:
        to_search = to_search.strip()
        current_user_posts = (Posts.query.filter_by(user_id = current_user.id)
        .filter(or_(Posts.title.ilike(f'%{to_search}%'),
        Posts.subject.ilike(f'%{to_search}%'),
        Posts.content.ilike(f'%{to_search}%'),
        )).order_by(Posts.date_posted.desc())
        .paginate(page = page, per_page = 5))
        if current_user_posts.total == 0:
            flash("Nothing related to your search was found.", "warning")
            return redirect(url_for("views.post"))
    else:
        current_user_posts = (Posts.query.filter_by(user_id = current_user.id)
        .order_by(Posts.date_posted.desc())
        .paginate(page = page, per_page = 5))

    return render_template("/post.html", current_user_posts = current_user_posts)

@views.route('/author/<int:id>/')
def author(id):
    author = User.query.get_or_404(id)
    page = request.args.get("page", 1, int)
    to_search = request.args.get("search")
    if to_search:
        to_search = to_search.strip()
        author_posts = (Posts.query.filter_by(user_id = author.id)
        .filter(or_(Posts.title.ilike(f'%{to_search}%'),
        Posts.subject.ilike(f'%{to_search}%'),
        Posts.content.ilike(f'%{to_search}%'),
        )).order_by(Posts.date_posted.desc())
        .paginate(page = page, per_page = 5))
        if author_posts.total == 0:
            flash("Nothing related to your search was found.", "warning")
            return redirect(url_for("views.author", id = author.id))
    else:
        author_posts = (Posts.query.filter_by(user_id = author.id)
        .order_by(Posts.date_posted.desc())
        .paginate(page = page, per_page = 5))
    return render_template("/author.html", author = author, author_posts = author_posts)

@views.route('/read_more/<int:id>')
def read_more(id):
    post = Posts.query.get_or_404(id)
    return render_template("/read_more.html", post = post)

@views.route('/update_post/<int:id>', methods = ['GET', 'POST'])
@login_required
def update_post(id):
    to_update_post = Posts.query.get_or_404(id)
    if to_update_post.author != current_user:
        abort(403)
    if request.method == "POST":
        subject = request.form.get("subject")
        title = request.form.get("title")
        content = request.form.get("content")

        to_update_post.subject = subject
        to_update_post.title = title
        to_update_post.content = content
        db.session.commit()
        flash("Post updated successfully.", "success")
        return redirect(url_for("views.post"))

    return render_template("/update_post.html", to_update_post = to_update_post)

    
@views.route('/delete_post/<int:id>')
@login_required
def delete_post(id):
    to_del_post = Posts.query.get_or_404(id)
    if to_del_post.author != current_user:
        abort(403)
    db.session.delete(to_del_post)
    db.session.commit()
    flash("Post deleted successfully.", "success")
    return redirect(url_for("views.post"))



