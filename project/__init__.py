from mimetypes import init
import os 
from flask import Flask
from flask_session import Session

def create_app():
    app = Flask(__name__)

    app.config['CLIENT_ID'] = os.getenv('CLIENT_ID')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    with app.app_context():
        # init_db()

        from .auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint)

        from .main import main as main_blueprint
        app.register_blueprint(main_blueprint)

    return app