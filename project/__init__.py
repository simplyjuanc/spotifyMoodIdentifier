import os 
from flask import Flask


def create_app():
    app = Flask(__name__)

    app.config['CLIENT_ID'] = os.getenv('CLIENT_ID')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    SECRET_KEY = app.config['SECRET_KEY']

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)


    return app