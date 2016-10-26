# coding: utf-8

import os
import flask
import json
from flask import Flask, send_from_directory
import server
from server.lib import GoogleAuth


class Config:
    """
    Default設定
    """
    ENV = ''
    DATABASE = ''
    DEBUG = True


def register_blueprints(app):
    """
    blueprint登録
    :param app:
    """
    from server.modules import (top, index, login)

    app.register_blueprint(index.module, url_prefix='/')
    app.register_blueprint(top.module, url_prefix='/top')
    app.register_blueprint(login.module, url_prefix='/login')

    @app.route('/')
    def index():
        return flask.redirect(flask.url_for('index.index'))

    @app.route('/static')
    def custom_static(file_name):
        return send_from_directory(app.config['STATIC_FOLDER'], file_name)


def make_app():
    """
    アプリケーション設定
    """
    env = os.environ.get('kelp', 'local')
    _config = None

    if env == 'local':
        from server.config.local import LocalConfig
        _config = LocalConfig

    if env == 'prod':
        from server.config.prod import ProdConfig
        _config = ProdConfig

    app = Flask(__name__, static_folder=_config.STATIC_FOLDER,
                static_url_path='/static')

    app.config.from_object(_config)

    return app


def init_web(app):
    """
    web初期化
    :param app:
    """
    register_blueprints(app)
    GoogleAuth().config(client_json=app.config['CLIENT_SECRET'],
                        redirect_url=app.config['GOOGLE_CALLBACK_URL'],
                        logger=app.logger)

    @app.context_processor
    def inject_path():
        sub_domain = flask.request.script_root
        return {
            'static_prefix': sub_domain + app.static_url_path,
        }

    @app.before_request
    def before_request():
        # flask.g.start = datetime.datetime.now()
        pass

    @app.teardown_request
    def write_accesslog(exc=None):
        """
        アクセスログを残すための設定
        """

        log = flask.g.get('start', None)
        if log is not None:
            # ToDo: Access log
            pass

    return app


def init(app):
    """
    アプリケーション初期化
    :param app:
    """
    server.app = app
    return app
