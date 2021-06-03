from instance.config import SECRET_KEY
from flask import Flask, config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail


mail = Mail()
db = SQLAlchemy()


#create flask app
def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # Add app.app_context() tp enable current_app to be used
    with app.app_context():
        app.config.from_object('config.Config')
        # app.config.from_pyfile('config.py')
        mail.init_app(app)
        db.init_app(app)

        login_manager = LoginManager()
        login_manager.login_view = "auth.login"
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
    
    
    
