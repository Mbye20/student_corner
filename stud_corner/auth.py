from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from .models import User
from . import db, app, mail

auth = Blueprint('auth', __name__)

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])



#Login Page
@auth.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Get the email and password
        email = request.form.get("email")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False

        user = User.query.filter_by(email=email).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))

        login_user(user, remember= remember)
        if user.confirmed == False:
            flash("Your email had not been confirmed. Please check your inbox to confirm your email address.", "danger")
            return redirect(url_for("login"))

        return redirect(url_for("views.index"))
        

    #Return login page if request is get
    return render_template("/login.html")

@auth.route("/logout")
@login_required
def logout():
    #Remove user from session and logout
    logout_user()
    #### session.pop('email', None)
    return redirect(url_for('views.index'))


@auth.route("/create_account", methods = ['POST', 'GET'])
def create_account():
    if request.method == "POST":
        #Get the data entered by the user
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        email = request.form.get("email")
        #Confirm if password matches
        if password1 != password2:
            flash("The passwords you entered do not match.", "error")
            return redirect(url_for("create_account"))
        #Min. Length of Password
        if len(password1) < 4:
            flash("Password should be atleast 8 characters.", "error")
            return redirect(url_for("create_account"))
        # Check if an account has already been created with the same email address
        user = User.query.filter_by(email=email).first()
        if user:
            flash("An account has already been created with this email address.", "error")
            return redirect(url_for("create_account"))

        new_user = User(firstname= firstname, lastname=lastname, email=email, password = generate_password_hash(password1), admin=False, confirmed=False, confirmed_on= None)
        # if new_user.confirmed == False:
        #     flash("An email has been sent to you email address. Please Click it to confirm your email address.")

        db.session.add(new_user)
        db.session.commit()

        token = serializer.dumps(email, salt = "confirm")
        link = url_for("confirm_email", token = token, _external = True)
        msg = Message("Email Confirmation", recipients = [new_user.email])
        msg.html = render_template("confirm.html", confirm_url = link)
        mail.send(msg)

        flash("An email has been sent to you email address. Please click it to activate your account.")
        return redirect(url_for('login'))
    
    return render_template("/create_account.html")



#     return email
#### Add a new route to handle the email confirmation
@auth.route("/confirm/<token>")
def confirm_email(token):
    try:
        email = serializer.loads(token, salt="confirm", max_age=7200)
    except:
        flash("The confirmation link is invalid or has expired.", "danger")
    user = User.query.filter_by(email = email).first_or_404()
    if user.confirmed and current_user.is_authenticated:
        flash("Your account had already been confirmed.")
        return redirect(url_for("views.index"))
    elif user.confirmed and not current_user.is_authenticated:
        flash("Your account had already been confirmed. Please login.")
    
    else:
        user.confirmed = True
        user.confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("Your account is successfully confirmed. Please enter your Email and Password to login.")

    return redirect(url_for("login"))

