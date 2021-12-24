from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from configurator import Config
from flask_migrate import Migrate
from flask_mail import Mail
from flask_googlemaps import GoogleMaps
from flask_moment import Moment
import logging
from logging.handlers import SMTPHandler
from flask_cdn import CDN
from elasticsearch import Elasticsearch
from flask_cors import CORS
from celery import Celery
# from flask_execute import Celery
from celery_worker import app as celery_worker

db = SQLAlchemy()  # creates a database instance from the SQLAlchemy library
migrate = Migrate()
bootstrap = Bootstrap()  # adds bootstrap to html
login = LoginManager()  # creates status var for state of login
login.login_view = 'auth.login'  # page for login page (similar to url_for())
login.login_message = 'Please log in to access this page.'
mail = Mail()
maps = GoogleMaps()
moment = Moment()
cors = CORS()
cdn = CDN()
# tailsman = Talisman()
# celery = Celery('')



def create_app(config_class=Config):
    application = Flask(__name__)
    application.config.from_object(config_class)
    db.init_app(application)
    migrate.init_app(application, db)
    bootstrap.init_app(application)
    login.init_app(application)
    login.login_view = 'auth.login'  # page for login page (similar to url_for())
    login.login_message = 'Please log in to access this page.'
    mail.init_app(application)
    maps.init_app(application)
    moment.init_app(application)
    cors.init_app(application)
    # celery.init_app(application)
    # celery.conf.update(application.config)
    __all__ = celery_worker

    # cdn.init_app(application)

    from app.errors import bp as errors_bp
    from app.errors.handlers import not_found_error, internal_error
    application.register_blueprint(errors_bp)
    application.register_error_handler(404, not_found_error)
    application.register_error_handler(500, internal_error)

    from app.auth import bp as auth_bp
    application.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    application.register_blueprint(main_bp)

    from app.background import bp as back_bp
    application.register_blueprint(back_bp, url_prefix='/bg')

    from app.partnership import bp as partner_bp
    application.register_blueprint(partner_bp, url_prefix='/p')

    from app.admin import bp as admin_bp
    application.register_blueprint(admin_bp, url_prefix='/admin')


    if not application.debug:
        if application.config['MAIL_SERVER']:
            auth = None
            if application.config['MAIL_USERNAME'] or application.config['MAIL_PASSWORD']:
                auth = (application.config['MAIL_USERNAME'], application.config['MAIL_PASSWORD'])
            secure = None
            if application.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(application.config['MAIL_SERVER'], application.config['MAIL_PORT']),
                fromaddr='no-reply@' + application.config['MAIL_SERVER'],
                toaddrs=application.config['ADMINS'], subject='ILMJTCV Program Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            application.logger.addHandler(mail_handler)


    # application.elasticsearch = Elasticsearch([application.config['ELASTICSEARCH_URL']]) \
    #     if application.config['ELASTICSEARCH_URL'] else None

    return application

from app import models