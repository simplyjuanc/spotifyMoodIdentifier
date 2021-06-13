import os 
from flask import Flask
from flask_session import Session

def create_app():
    app = Flask(__name__)

    app.config['CLIENT_ID'] = os.getenv('CLIENT_ID')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app