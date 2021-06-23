from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate



mail = Mail()
db = SQLAlchemy()
migrate = Migrate()

#create flask app
def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=False)
    # Add app.app_context() to enable current_app to be used
    with app.app_context():
        # Do not forget changing to dev config while working locally
        from config import Config
        app.config.from_object(Config())
        app.jinja_env.trim_blocks = True
        app.jinja_env.lstrip_blocks = True

        mail.init_app(app)
        db.init_app(app)
        migrate.init_app(app, db)

        login_manager = LoginManager()
        login_manager.login_view = "auth.signin"
        login_manager.login_message = u"Please sign in to access this page."
        login_manager.login_message_category = "warning"
        login_manager.init_app(app)

        from .models import User
        #Add user loader to retrieve user id from the database for user login
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        from .views import views
        from .auth import auth
        app.register_blueprint(views)
        app.register_blueprint(auth)



    return app