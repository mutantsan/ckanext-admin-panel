from __future__ import annotations

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ckan.plugins import toolkit as tk

from ckanext.admin_panel.model import ApLogs
from ckanext.admin_panel.utils import add_log_type

log = logging.getLogger(__name__)


class DatabaseHandler(logging.Handler):
    not_ready = False

    def __init__(self, db_uri: str, redis_uri: str):
        super().__init__()

        engine = create_engine(db_uri)

        if not engine.has_table(ApLogs.__tablename__):
            self.not_ready = True
            log.error("The ApLogs table is not initialized")

        Session = sessionmaker(bind=engine)
        ApLogs.set_session(Session())
        ApLogs.set_redis_uri(redis_uri)

    def emit(self, record):
        if not tk.config:
            return

        if self.not_ready:
            return

        add_log_type(record.name)

        ApLogs.save_log(record, self.format(record))
