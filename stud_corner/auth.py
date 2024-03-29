from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from .models import User
from . import db
from .tokens import generate_confirmation_token, confirm_token, generate_renew_password_token, confirm_renew_password_token
from .email import send_email

auth = Blueprint('auth', __name__)



#Login Page
@auth.route("/signin", methods = ['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        flash("Sorry, you are already signed in.", "info")
        return redirect(url_for("views.index"))

    if request.method == 'POST':
        #Get the email and password
        email = request.form.get("email")
        password = request.form.get("password")
        if request.form.get("remember"):
            remember = True  
        else:
            remember = False

        user = User.query.filter_by(email=email).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user:
            flash("You entered an invalid email.", "info")
            return redirect(url_for("auth.signin"))
        if not check_password_hash(user.password, password):
            flash("You entered an invalid password.", "info")
            flash("Forgot your password? ", "password-alert")
            return redirect(url_for("auth.signin"))

        if not user.confirmed:
            flash(
                "Your email had not been confirmed. Please check your inbox to confirm your email address and sign in again. Didn't get the email?",
                "unconfirmed_email"
                )
            logout_user()
            return redirect(url_for("auth.signin"))

        login_user(user, remember= remember)
        return redirect(url_for("views.index"))
        
    #Return login page if request is get
    return render_template("/signin.html")

@auth.route("/signout")
@login_required
def signout():
    #Remove user from session and logout
    logout_user()
    return redirect(url_for('auth.signin'))


@auth.route("/signup", methods = ['POST', 'GET'])
def signup():
    if current_user.is_authenticated:
        flash("Sorry, you are already login.", "info")
        return redirect(url_for("views.index"))
    if request.method == "POST":
        #Get the data entered by the user
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        email = request.form.get("email")
        #Confirm if password matches
        if password1 != password2:
            flash("The passwords you entered do not match.", "info")
            return redirect(url_for("auth.signup"))
        #Min. Length of Password
        if len(password1) < 4:
            flash("Password should be atleast 4 characters.", "info")
            return redirect(url_for("auth.signup"))
        # Check if an account has already been created with the same email address
        user = User.query.filter_by(email=email).first()
        if user:
            flash("An account has already been created with this email address.", "info")
            return redirect(url_for("auth.signup"))

        new_user = User(
            firstname= firstname,
            lastname=lastname,
            email=email, password = generate_password_hash(password1)
            )
        
        db.session.add(new_user)
        db.session.commit()

        token = generate_confirmation_token(new_user.email)
        confirm_url = url_for("auth.confirm_email", token = token, _external = True)
        subject = "Email Confirmation"
        html = render_template("confirm.html", confirm_url = confirm_url)

        send_email(new_user.email, subject, html)

        flash(
            "An email has been sent to you email address. Please click it to activate your account.",
            "success"
            )
        return redirect(url_for('auth.signin'))
    
    return render_template("/signup.html")



#     return email
#### Add a new route to handle the email confirmation
@auth.route("/confirm/<token>")
def confirm_email(token):
    try:
        email = confirm_token(token)

        user = User.query.filter_by(email = email).first_or_404()
        if user.confirmed and current_user.is_authenticated:
            flash("Your account had already been confirmed.", "success")
            return redirect(url_for("views.index"))
        elif user.confirmed and not current_user.is_authenticated:
            flash("Your account had already been confirmed. Please sign in.", "success")
        
        else:
            user.confirmed = True
            user.confirmed_on = datetime.now()
            db.session.add(user)
            db.session.commit()
            flash(
                "Your account is successfully confirmed. Please enter your Email and Password to sign in.",
                "success"
                )

            return redirect(url_for("auth.signin"))
    except:
        return redirect(url_for("auth.error"))

@auth.route('/resend_confirmation', methods = ['POST', 'GET'])
def resend_confirmation():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            # Check if the user is already confirmed
            if user.confirmed:
                flash('Your Email address is already confirmed. Please sign in.', 'info')
                return redirect(url_for('auth.signin'))
            token = generate_confirmation_token(email)
            confirm_url = url_for('auth.confirm_email', token=token, _external=True)
            html = render_template('confirm.html', confirm_url=confirm_url)
            subject = "Email Confirmation"
            send_email(user.email, subject, html)
            flash('A new confirmation email has been sent.', 'success')
            return redirect(url_for('auth.signin'))
        else:
            flash("You entered an invalid email.", "info")
            return redirect(url_for("auth.resend_confirmation"))
    return render_template("enter_email.html", title = "Resend Email Confirmation Link")




@auth.route("/reset_password_request", methods = ['POST', 'GET'])
def reset_password_request():
    if request.method == 'POST':
        #Get the user email
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_renew_password_token(email)
            reset_password_url = url_for('auth.reset_password_form', token=token, _external=True)
            html = render_template('renew_password.html', reset_password_url=reset_password_url)
            subject = "Password Renewal Link"
            send_email(user.email, subject, html)
            flash("An email with a link to renew your password has been sent to your email address.", "success")
        else:
            flash("You entered an invalid email.", "info")

    return render_template("enter_email.html", title = "Reset Password Request")


@auth.route("/reset_password_form/<token>", methods = ['POST', 'GET'])
def reset_password_form(token):
    if request.method == 'POST':
        try:
            email = confirm_renew_password_token(token)

            password1 = request.form.get("password1")
            password2 = request.form.get("password2")
            if password1 != password2:
                flash("The passwords you entered do not match.", "info")
                return redirect(url_for("auth.reset_password_form", token=token))
            #Min. Length of Password
            if len(password1) < 4:
                flash("Password should be atleast 4 characters.", "info")
                return redirect(url_for("auth.reset_password_form", token=token))
            
            user = User.query.filter_by(email = email).first_or_404()
            user.password = generate_password_hash(password1)
            db.session.commit()
            flash(
                "Your password is successfully renewed. Please enter your email and new Password to sign in.",
                "success"
                )
        except:
            flash(
                "The password renewal link is invalid or has expired. Enter your email address again to receive a new link.",
                "danger"
                )
            return redirect(url_for("auth.reset_password_request"))
        return redirect(url_for("auth.signin"))

    return render_template("reset_password_form.html")

    
@auth.route('/error')
def error():
    return render_template("error.html")




