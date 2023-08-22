import logging

from sqlalchemy import engine_from_config, inspect
from sqlalchemy.exc import UnboundExecutionError

from ckan import model
from ckan.plugins import toolkit as tk

from ckanext.admin_panel.model import ApLogs


class DatabaseHandler(logging.Handler):
    def emit(self, record):
        log_message = self.format(record)

        if not tk.config:
            return

        engine = engine_from_config(tk.config)

        if not inspect(engine).has_table(ApLogs.__tablename__):
            return

        try:
            ApLogs.save_log(record, log_message)
        except UnboundExecutionError:
            model.Session.rollback()
