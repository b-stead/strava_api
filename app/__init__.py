import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_login import LoginManager
#from flask_mail import Mail
#from flask_bootstrap import Bootstrap
#from flask_moment import Moment
#from flask_babel import Babel, lazy_gettext as _l
from config import Config


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['OAUTH2_PROVIDERS'] = {
    'strava': {
        'client_id': os.getenv('STRAVA_CLIENT_ID'),
        'client_secret': os.getenv('STRAVA_CLIENT_SECRET'),
        'authorize_url': 'https://www.strava.com/oauth/authorize',
        'token_url': 'https://www.strava.com/oauth/token',
        'userinfo': {
            'url': 'https://www.strava.com/api/v3/athlete',
            'username': lambda json: json[5]['username'],
        },
        'scopes': 'read_all',
        },
    }

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    #mail.init_app(app)
    #bootstrap.init_app(app)
    #moment.init_app(app)
    #babel.init_app(app)

    #from app.errors import bp as errors_bp
    #app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.clubs import bp as clubs_bp
    app.register_blueprint(clubs_bp, url_prefix='/clubss')

    from app.strava import bp as strava_bp
    app.register_blueprint(strava_bp)

    return app

from app import models
