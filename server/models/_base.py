# coding: utf-8
from sqlalchemy import MetaData
from sqlalchemy.orm import object_session
from ._db import SessionManager
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.util import identity_key
from collections import OrderedDict
import datetime


class MasterDataException(Exception):
    """
    マスター取得時のエラー
    """
    pass


class BadColumnTypeException(Exception):
    pass


class AsDictMixin(object):

    def as_dict(self, include=None, exclude=None):
        to_expand = set()
        if hasattr(self, 'json_keys'):
            to_expand.update(self.json_keys)
        if exclude is not None:
            to_expand.difference_update(exclude)
        if include is not None:
            to_expand.update(include)

        print('AsDictMixin', to_expand)

        return {k: _to_jsonable(getattr(self, k)) for k in to_expand}

db = SessionManager()
class_registry = {}
_BaseDeclarative = declarative_base(class_registry=class_registry,
                                    metadata=MetaData())


class _BaseModel(_BaseDeclarative):

    __abstract__ = True

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_default_charset': 'utf8mb4'
    }

    metadata = None
    default_session_name = 'database_session'

    @classmethod
    def query(cls, session_name=None):
        """
        :rtype: .database.Query
        """
        return db.session(session_name or cls.default_session_name).query(cls)

    def __repr__(self):
        return self.__unicode__().encode('utf8', 'replace')

    def __unicode__(self):
        columns = self.__table__.columns.keys()
        print('columns', columns)
        return u'{}({})'.format(self.__class__.__name__,
                                ', '.join(u'{}={}'.format(c, getattr(self, c)) for c in columns))

    def lock(self):
        session = object_session(self)
        assert not session.is_modified(self), "ロックする前に、flushしてください。"
        session.refresh(self, lockmode="update")

    @classmethod
    def add_new(cls, _session_name=None, **kw):
        instance = cls(**kw)
        db.session(_session_name or cls.default_session_name).add(instance)
        return instance


class Base(_BaseModel, AsDictMixin):
    __abstract__ = True

    metadata = MetaData()
    default_session_name = 'database_session'


def _to_jsonable(obj):
    if hasattr(obj, 'as_dict'):
        return obj.as_dict()

    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple)):
        return map(_to_jsonable, obj)

    if isinstance(obj, (int, float, datetime.datetime, datetime.date)):
        return obj

    if obj is None:
        return None

    raise TypeError("jsonableの値に変換できません: {!r}".format(obj))


class BaseMaster(Base):

    __abstract__ = True
    __client_db__ = False

    @classmethod
    def _primary_key_from_instance(cls, obj):
        _identity_key = cls.__mapper__.identity_key_from_instance(obj)
        return _identity_key[1]

    @classmethod
    def _primary_key_from_ident(cls, ident):
        _identity_key = identity_key(cls, ident)
        return _identity_key[1]

    @classmethod
    def _load_data(cls):
        cls._identity_map = OrderedDict()
        rows = cls.query().all()
        for row in rows:
            db.session().expunge(row)
            cls._identity_map[cls._primary_key_from_instance(row)] = row

    @classmethod
    def load_data(cls):
        if not hasattr(cls, '_identity_map'):
            cls._load_data()
        elif not cls._identity_map:
            cls._load_data()

    @classmethod
    def _get_idmap(cls):
        cls._load_data()
        return cls._identity_map

    @classmethod
    def all(cls):
        idmap = cls._get_idmap()
        return idmap.values()

    @classmethod
    def get(cls, ident):
        idmap = cls._get_idmap()
        primary_key = cls._primary_key_from_ident(ident)
        return idmap.get(primary_key)

    @classmethod
    def get_one(cls, ident):
        idmap = cls._get_idmap()
        primary_key = cls._primary_key_from_ident(ident)
        obj = idmap.get(primary_key)
        if not obj:
            raise MasterDataException('Row not found. {}, {}'.format(cls, ident))
        return obj

    @classmethod
    def filter_by(cls, **kwargs):
        def _filter(row):
            for col_name, value in kwargs.items():
                col_value = row.__dict__[col_name]
                if isinstance(value, (tuple, list)):
                    if col_value not in value:
                        return False
                elif col_value != value:
                    return False
            return True
        objs = cls.all()

        return filter(_filter, objs)

    @classmethod
    def filter_first(cls, **kwargs):
        objs = cls.filter_by(**kwargs)
        if len(objs) == 0:
            return None
        return objs[0]

    @classmethod
    def filter_one(cls, **kwargs):
        objs = cls.filter_by(**kwargs)
        if len(objs) == 0:
            raise MasterDataException('Row not found. {}, {}'.format(cls, kwargs))
        return objs[0]

    def as_ordered_dict(self, exclude=()):
        """
        here to_expand is a list but not a set
        so as to keep the order
        """
        to_expand = self.__table__.columns.keys()
        d = OrderedDict()
        for k in to_expand:
            if k not in exclude:
                d[k] = getattr(self, k)
        return d

    @classmethod
    def get_primary_keys(cls):
        return cls.__table__.primary_key

    @classmethod
    def from_text(cls, **kwargs):
        for k, v in kwargs.items():
            kwargs[k] = cls.type_coherence(k, v)
        return cls(**kwargs)

    @classmethod  # noqa
    def type_coherence(cls, k, v):
        column = cls.__table__.columns[k]
        column_type = column.type

        # マスターデータを TSV ではなく JSON から読み込む場合.
        if v is None:
            if not column.nullable:
                raise TypeError("Column %r is not nullable" % (k,))
            return None

        if column_type.python_type is int:
            if v is not None:
                return int(v)
            if column.nullable is True:
                return None
            raise ValueError("Error in column (%s): "
                             "Integer value must not be empty." % column.key)

        if column_type.python_type is float:
            if v is not None:
                return float(v)
            if column.nullable is True:
                return None
            raise ValueError("Error in column (%s): "
                             "Integer value must not be empty." % column.key)

        if column_type.python_type in (datetime.datetime, datetime.date):
            if v is not None:
                return v
            if column.nullable is True:
                return None
            raise ValueError("Error in column (%s): "
                             "Integer value must not be empty." % column.key)

        if column_type.python_type is str:
            if column.nullable is False and len(v) == 0:
                raise ValueError("Error in column (%s): "
                                 "String value must not be empty." % column.key)
            return v

        if column_type.python_type is bool:
            if v == '0' or v is False:
                return False
            elif v == '1' or v is True:
                return True
            else:
                raise ValueError("Error in column (%s): "
                                 "bool should be '0' or '1': %r" % (column.key, v))

        raise BadColumnTypeException()
