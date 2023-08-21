from __future__ import annotations

import logging
from typing import Any
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.orm import Query

import ckan.model as model
from ckan.model.types import make_uuid
from ckan.plugins import toolkit as tk


log = logging.getLogger(__name__)


class ApLogs(tk.BaseModel):
    __tablename__ = "ap_logs"

    class Level:
        NOTSET = 0
        DEBUG = 10
        INFO = 20
        WARNING = 30
        ERROR = 40
        CRITICAL = 50

    id = Column(Text, primary_key=True, default=make_uuid)

    name = Column(Text)
    path = Column(Text)
    level = Column(Integer)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    message = Column(Text)
    message_formatted = Column(Text)

    @classmethod
    def all(cls) -> list[dict[str, Any]]:
        query: Query = model.Session.query(cls).order_by(cls.timestamp.desc())

        return [log.dictize({}) for log in query.all()]

    @classmethod
    def save_log(cls, record: logging.LogRecord, message_formatted: str) -> None:
        log = cls(
            name=record.name,
            path=record.pathname,
            level=record.levelno,
            message=record.msg,
            message_formatted=message_formatted,
        )

        model.Session.add(log)
        model.Session.commit()

    def dictize(self, context):
        return {
            "name": self.name,
            "path": self.path,
            "level": self.level,
            "timestamp": self.timestamp,
            "message": self.message,
            "message_formatted": self.message_formatted,
        }

    @classmethod
    def clear_logs(cls) -> int:
        rows_deleted = model.Session.query(cls).delete()
        model.Session.commit()

        return rows_deleted
