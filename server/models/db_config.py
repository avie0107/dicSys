# coding: utf-8

import flask
from sqlalchemy import create_engine


def get_engine():
    """
    engine取得
    """
    app = flask.current_app
    if not hasattr(app, 'engine'):
            app.engine = create_engine(app.config['DATABASE_ENGINES'])
    return app.engine


def init_db(echo=True):
    """
    データベース初期化、boomerang.scriptで呼ばれる
    :param echo: (処理結果を画面で表示する)
    """
    from server.models import table_models
    engine = get_engine()
    engine.echo = echo
    table_models.BaseMaster.metadata.create_all(engine)
