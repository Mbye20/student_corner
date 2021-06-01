import os
import re
from os import environ
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_login import UserMixin, login_manager, login_user, LoginManager, logout_user, current_user
from datetime import timedelta, datetime
from flask_login.utils import login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask_migrate import Migrate
load_dotenv()
#create flask app
app = Flask(__name__)
####Configure Email Credential
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = ("Student Corner Web", environ.get('MAIL_USERNAME'))

#Register mail on app
mail = Mail(app)
#Give a secrete for the session and flashing
app.secret_key = environ.get("SECRET_KEY")
#Create a security password for flask_mail
# SECURITY_PASSWORD_SALT = environ.get("SECURITY_PASSWORD_SALT")
#Configure session timelimit
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
####Postgresql Database
database_uri = environ.get('DATABASE_URL')
if database_uri.startswith("postgres://"):
    database_uri = database_uri.replace("postgres://", "postgresql://", 1)

#Configure database
#### Configure postgresql database to run om server and sqlite to run on local host
app.config['SQLALCHEMY_DATABASE_URI']= database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

login_manager = LoginManager()
login_manager.init_app(app)


#Create a user model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, default=datetime.now, nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120))
    admin = db.Column(db.Boolean, nullable=False, default=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    
    def __init__(self, firstname, lastname, email, password, admin, confirmed, confirmed_on):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.admin = admin
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on

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

#Main page
@app.route('/')
def index():
    return render_template("/index.html")

#Login Page
@app.route("/login", methods = ['GET', 'POST'])
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

        session.permanent = True
        #Send Message through gmail to user after log in
        # msg = Message("Hello %s, " %user.firstname, recipients= [user.email])
        # msg.body = "You have been Logged in successfully. Cheers!"
        # mail.send(msg)
        ### session["email"] = email
        login_user(user, remember= remember)
        if user.confirmed == False:
            flash("Your email had not been confirmed. Please check your inbox to confirm your email address.", "danger")
            return redirect(url_for("login"))

        return redirect(url_for("index"))
        

    #Return login page if request is get
    return render_template("/login.html")

@app.route("/logout")
@login_required
def logout():
    #Remove user from session and logout
    logout_user()
    #### session.pop('email', None)
    return redirect(url_for('index'))


@app.route("/create_account", methods = ['POST', 'GET'])
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
        
        #For user email confirmation token
        # token = generate_confirmation_token(user.email)

        # confirm_url = url_for("confirm_email", token = token, _external = True)
        # html = render_template("confirm.html", confirm_url = confirm_url)
        # subject = "Email Confirmation"

        # send_email(user.email, subject, html)

        #### print(User.query.order_by(User.username).all())
        # flash('A confirmation email has been sent via email.', 'success')
        

    
    return render_template("/create_account.html")


#### Create token generator function
# def generate_confirmation_token(email):
#     return serializer.dumps(email, salt= "activate")

# def confirm_token(token):
#     try:
#         email = serializer.loads(token, salt="activate", max_age=7200)
    
#     except:
#         return False
#     return email
#### Add a new route to handle the email confirmation
@app.route("/confirm/<token>")
def confirm_email(token):
    try:
        email = serializer.loads(token, salt="confirm", max_age=7200)
    except:
        flash("The confirmation link is invalid or has expired.", "danger")
    user = User.query.filter_by(email = email).first_or_404()
    if user.confirmed and current_user.is_authenticated:
        flash("Your account had already been confirmed.")
        return redirect(url_for("index"))
    elif user.confirmed and not current_user.is_authenticated:
        flash("Your account had already been confirmed. Please login.")
    
    else:
        user.confirmed = True
        user.confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("Your account is successfully confirmed. Please enter your Email and Password to login.")

    return redirect(url_for("login"))

# def send_email(to, subject, template):
#     msg = Message(
#         subject,
#         recipients= [to],
#         html=template,
#     )
#     mail.send(msg)



@app.route('/profile')
@login_required
def profile():
    return render_template("/profile.html", firstname=current_user.firstname)

@app.route('/post')
@login_required
def post():
    return render_template(url_for("post"))





if __name__ == "__main__":
    db.create_all()
    app.run(debug=False)
