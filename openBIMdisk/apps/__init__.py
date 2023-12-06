# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from flask_dropzone import Dropzone



db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'home'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.config.update(
        DROPZONE_ALLOWED_FILE_TYPE="default",
        DROPZONE_INPUT_NAME='file',
        DROPZONE_PARALLELUPLOADS = 2,
        DROPZONE_ADDREMOVELINKS = True,
        DROPZONE_TIMEOUT = 5000,
        DROPZONE_UPLOAD_MULTIPLE = True,
        DROPZONE_REDIRECT_VIEW = '/tsdt_function',
        # DROPZONE_AUTOPROCESS_QUEUE = False,
    )
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    dropzone = Dropzone(app)
    return app
