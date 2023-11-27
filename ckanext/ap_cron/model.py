from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from typing_extensions import Self

from sqlalchemy import Column, DateTime, Text
from sqlalchemy.orm import Query
from sqlalchemy.dialects.postgresql import JSONB

import ckan.model as model
from ckan.model.types import make_uuid
from ckan.plugins import toolkit as tk

from ckanext.ap_main.types import CronJobData

log = logging.getLogger(__name__)



class ApCronJob(tk.BaseModel):
    __tablename__ = "ap_cron_job"

    class State:
        active = "active"
        disabled = "disabled"
        pending = "pending"
        running = "running"

    id = Column(Text, primary_key=True, default=make_uuid)

    name = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_run = Column(DateTime, nullable=True)
    schedule = Column(Text)
    data = Column(JSONB, nullable=False)
    state = Column(Text)

    @classmethod
    def all(cls) -> list[dict[str, Any]]:
        query: Query = model.Session.query(cls).order_by(cls.last_run.desc())

        return [job.dictize({}) for job in query.all()]

    @classmethod
    def get(cls, job_id: str) -> Self | None:
        query: Query = model.Session.query(cls).filter(cls.id == job_id)

        return query.one_or_none()

    def delete(self) -> None:
        model.Session().autoflush = False
        model.Session.delete(self)

    @classmethod
    def add(cls, job: CronJobData) -> None:
        model.Session.add(
            cls(
                name=job["name"],
                schedule=job["schedule"],
                data=job["data"],
            )
        )
        model.Session.commit()

    def dictize(self, context):
        return {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_run": self.last_run.isoformat(),
            "schedule": self.schedule,
            "data": self.data,
        }
