from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, ClassVar
from unittest import mock

from sqlalchemy import Column, DateTime, Integer, Text, Index
from sqlalchemy.orm import Query, Session

from ckan.plugins import toolkit as tk

log = logging.getLogger(__name__)


class ApLogs(tk.BaseModel):
    __tablename__ = "ap_logs"
    session: ClassVar[Session] = mock.MagicMock()
    redis_uri: ClassVar[str] = ""

    class Level:
        NOTSET = 0
        DEBUG = 10
        INFO = 20
        WARNING = 30
        ERROR = 40
        CRITICAL = 50

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    name = Column(Text)
    path = Column(Text)
    level = Column(Integer)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    message = Column(Text)
    message_formatted = Column(Text)

    @classmethod
    def all(cls) -> list[dict[str, Any]]:
        # TODO: delete due to ineffectiveness
        # currently, we are using it only to collect log type options
        query: Query = cls.session.query(cls).order_by(cls.timestamp.desc())

        return [log.dictize({}) for log in query.all()]

    @classmethod
    def save_log(cls, record: logging.LogRecord, message_formatted: str) -> None:
        cls.session.add(
            cls(
                name=record.name,
                path=record.pathname,
                level=record.levelno,
                message=record.getMessage(),
                message_formatted=message_formatted,
            )
        )
        cls.session.commit()

    def dictize(self, context):
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "level": self.level,
            "timestamp": self.timestamp,
            "message": self.message,
            "message_formatted": self.message_formatted,
        }

    @classmethod
    def clear_logs(cls) -> int:
        rows_deleted = cls.session.query(cls).delete()
        cls.session.commit()

        return rows_deleted

    @classmethod
    def set_session(cls, session: Session):
        cls.session = session

    @classmethod
    def set_redis_uri(cls, redis_uri: str):
        cls.redis_uri = redis_uri

    @classmethod
    def get_session(cls) -> Session:
        return cls.session

    @classmethod
    def table_initialized(cls) -> bool:
        if not cls.session:
            return False

        engine = cls.session.get_bind()
        return engine.has_table(cls.__table__)
