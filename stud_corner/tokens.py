from flask import current_app
from itsdangerous import URLSafeTimedSerializer

serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def generate_confirmation_token(email):
    return serializer.dumps(email, salt="confirm-email")


def confirm_token(token, expiration=7200):
    try:
        email = serializer.loads(
            token,
            salt="confirm-email",
            max_age=expiration
        )
    except:
        return False
    return email


def generate_renew_password_token(email):
    return serializer.dumps(email, salt="renew-password")


def confirm_renew_password_token(token, expiration=7200):
    try:
        email = serializer.loads(
            token,
            salt="renew-password",
            max_age=expiration
        )
    except:
        return False
    return email