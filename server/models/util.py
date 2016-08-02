#coding: utf-8

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.schema import Index as _Index
from sqlalchemy.schema import UniqueConstraint
from server.lib.time_lib import now_timestamp as now
from . import BaseMaster


def created_at(**kw):
    return Column(DATETIME, nullable=False, default=now, **kw)


def updated_at(**kw):
    return Column(DATETIME, nullable=False, default=now, onupdate=now, **kw)


def unique(*column_names):
    name = 'ux_' + '_'.join(column_names)
    return UniqueConstraint(*column_names, name=name)


def index(*column_names):
    name = 'ix_' + '_'.join(column_names)
    return _Index(name, *column_names)


def get_class_by_tablename(tablename):

    for class_name in BaseMaster._decl_class_registry.values():
        if hasattr(class_name, '__tablename__') and class_name.__tablename__ == tablename:
            return class_name


def get_column_data_type(class_, colname):
    if hasattr(class_, '__table__') and colname in class_.__table__.c:
        return class_.__table__.c[colname].type

    raise NameError(colname)
