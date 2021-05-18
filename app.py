from flask import Flask, escape, request, render_template, redirect, url_for, flash, session
from datetime import timedelta
app = Flask(__name__)
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

app.secret_key = b'k\xb2\xefS\xd5\xe2DA\xf3uw\xa9\xc0\xce\xc67'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
users = []

@app.route('/')
def index():
    if 'email' in session:
        return render_template("/index.html")
    return render_template("/index.html")

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        session.permanent = True
        session["email"] = email

        return redirect(url_for("index"))
    return render_template("/login.html")

@app.route("/logout")
def logout():
   session.pop('email', None)
   return redirect(url_for('index'))

@app.route("/create_account", methods = ['POST', 'GET'])
def create_account():
    if request.method == "POST":
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        if password1 != password2:
            flash("The passwords you entered do not match.")
            return redirect(url_for("create_account"))
        user = request.form.get("firstname")
        users.append(user)
        print(users)
        return redirect(url_for('index'))
    
    else:
        return render_template("/create_account.html")
    






if __name__ == "__main__":
    app.run(debug=True)