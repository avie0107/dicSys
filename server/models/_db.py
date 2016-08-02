import logging
import time
import boomerang
from sqlalchemy import inspect
from operator import itemgetter
from sqlalchemy import create_engine
from flask import _app_ctx_stack
from sqlalchemy.event import listen
from sqlalchemy.orm import Session, scoped_session, sessionmaker, exc
from flask.ext.sqlalchemy import BaseQuery


class Query(BaseQuery):
    def get_one(self, ident, notfound=exc.NoResultFound):
        """一つのレコードを取得する(by PK)
        When no result found, raises `notfound` when it is not None.
        When `notfound` is None, returns None.
        """
        ret = self.get(ident)
        if ret is None and notfound is not None:
            raise notfound
        return ret

    def first_one(self, notfound=exc.NoResultFound):
        """最初のレコードだけを取得する
        When no result found, raises `notfound` when it is not None.
        When `notfound` is None, returns None.
        """
        ret = self.first()
        if ret is None and notfound is not None:
            raise notfound
        return ret

    def get_all(self):
        """
        全部のレコードを取得
        :return:
        """

        ret = self.all()
        for rec in ret:
            mapper = inspect(rec)
            for columns in mapper.attrs:
                print(columns.key)
        return ret


class SessionManager(object):
    _sessions = None
    init = False

    def _create_session(self, name):
        """
        :param str name: name of database.
        """
        engine = create_engine(name, pool_recycle=3600, encoding='utf-8')
        _EngineDebuggingSignalEvents(engine).register()
        session = scoped_session(sessionmaker(
            bind=engine, class_=Session,
            expire_on_commit=False, query_cls=Query))
        self._sessions['database_session'] = session

    def exit_sessions(self, response_or_exc=None):
        """全ての Session を終了する.
        commit されていない変更は全て rollback される.
        引数は Flask.teardown_appcontext() から呼ばれる場合に渡される.
        """
        for sess in list(self._sessions.values()):
            sess.remove()
        return response_or_exc

    def init_app(self, app):
        """
        :type app: flask.Flask
        """
        self.init = True
        self._sessions = {}
        self._init_sessions(app)

        app.teardown_appcontext(self.exit_sessions)

    def init_webapp(self, app):
        # テスト時はテスト側でセッションの寿命を管理する.
        if not app.testing:
            app.teardown_appcontext(self.exit_sessions)

    def _init_sessions(self, app):
        echo = app.config.get('DATABASE_ECHO')
        if echo == "debug":
            logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
        elif echo:
            logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

        self._create_session(boomerang.app.config["DATABASE_ENGINES"])

    def get_session(self, name='database_session'):
        """
        :param str name: Name of session
        :rtype: sqlalchemy.orm.Session
        """
        return self._sessions[name]

    session = get_session


class _DebugQueryTuple(tuple):

    statement = property(itemgetter(0))
    parameters = property(itemgetter(1))
    start_time = property(itemgetter(2))
    end_time = property(itemgetter(3))

    @property
    def duration(self):
        return self.end_time - self.start_time

    def __repr__(self):
        return '<query statement="%s" parameters=%r duration=%.03f>' % (
            self.statement,
            self.parameters,
            self.duration
        )


class _EngineDebuggingSignalEvents(object):
    """Sets up handlers for two events that let us track the execution time of queries."""

    def __init__(self, engine):
        self.engine = engine

    def register(self):
        listen(self.engine, 'before_cursor_execute', self.before_cursor_execute)
        listen(self.engine, 'after_cursor_execute', self.after_cursor_execute)

    def before_cursor_execute(self, conn, cursor, statement,
                              parameters, context, executemany):
        if _app_ctx_stack.top is not None:
            context._query_start_time = time.time()

    def after_cursor_execute(self, conn, cursor, statement,
                             parameters, context, executemany):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            queries = getattr(ctx, 'sqlalchemy_queries', None)
            if queries is None:
                queries = []
                setattr(ctx, 'sqlalchemy_queries', queries)
            queries.append(_DebugQueryTuple((
                statement, parameters, context._query_start_time, time.time())))


def get_debug_queries():
    return getattr(_app_ctx_stack.top, 'sqlalchemy_queries', [])
