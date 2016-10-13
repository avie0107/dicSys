#coding: utf-8

from sqlalchemy import (Column, Index, UniqueConstraint, Text)
from sqlalchemy.dialects.mysql import (INTEGER, SMALLINT, VARCHAR)
from sqlalchemy.dialects.mysql import DATETIME
from server.lib.time_lib import now_timestamp
from server.models.util import created_at, updated_at
from server.models import BaseMaster


class User(BaseMaster):
    __tablename__ = 'user'

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(VARCHAR(64), nullable=False, server_default='')
    email = Column(VARCHAR(64), server_default='', nullable=False, unique=True)
    authority_type = Column(SMALLINT, default=3)
    current_project_id = Column(INTEGER(unsigned=True), default=0)
    email_flag = Column(SMALLINT, default=0)
    locale = Column(VARCHAR(20), server_default='ja_JP.UTF-8')
    last_login = Column(DATETIME, nullable=True, default=now_timestamp)
    delete_flag = Column(SMALLINT, default=0)
    deleted = Column(DATETIME, nullable=True)
    created = created_at()
    updated = updated_at()

    __table_args__ = ({'mysql_charset': 'utf8mb4'})

    def __repr__(self):
        return "<id={} email={}>".format(self.id, self.email)
