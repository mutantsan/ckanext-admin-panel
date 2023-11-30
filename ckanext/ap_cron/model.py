from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional
from typing_extensions import Self

from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB

import ckan.model as model
from ckan.model.types import make_uuid
from ckan.plugins import toolkit as tk

from ckanext.ap_cron.types import CronJobData, DictizedCronJob
from ckanext.ap_cron import config as cron_conf

log = logging.getLogger(__name__)


class CronJob(tk.BaseModel):
    __tablename__ = "ap_cron_job"

    class State:
        active = "active"
        disabled = "disabled"
        pending = "pending"
        running = "running"
        failed = "failed"

    id = Column(Text, primary_key=True, default=make_uuid)

    name = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_run = Column(DateTime, nullable=True)
    schedule = Column(Text)
    actions = Column(Text)
    data: dict[str, Any] = Column(JSONB, nullable=False)  # type: ignore
    state = Column(Text, default=State.active)
    timeout = Column(Integer, default=cron_conf.get_job_timeout())

    @classmethod
    def get(cls, job_id: str) -> Self | None:
        query = model.Session.query(cls).filter(cls.id == job_id)

        return query.one_or_none()

    @classmethod
    def get_list(cls, state: Optional[str] = None) -> list[DictizedCronJob]:
        query = model.Session.query(cls)

        if state:
            query = query.filter(cls.state == state)

        query = query.order_by(cls.last_run.desc())

        return [job.dictize({}) for job in query.all()]

    def delete(self) -> None:
        model.Session().autoflush = False
        model.Session.delete(self)

    @classmethod
    def add(cls, job_data: CronJobData) -> DictizedCronJob:
        job = cls(
            name=job_data["name"],
            schedule=job_data["schedule"],
            actions=", ".join(job_data["actions"]),
            data=job_data["data"],
            timeout=job_data["timeout"],
        )

        model.Session.add(job)
        model.Session.commit()

        return job.dictize({})

    def dictize(self, context) -> DictizedCronJob:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "schedule": self.schedule,
            "actions": self.get_actions,
            "data": self.data,
            "state": self.state,
            "timeout": self.timeout,
        }

    @property
    def get_actions(self):
        return (
            self.actions.split(",") if isinstance(self.actions, str) else self.actions
        )
