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
from ckanext.ap_cron.const import KWARGS
from ckanext.ap_cron import config as cron_conf

log = logging.getLogger(__name__)


class CronJob(tk.BaseModel):
    __tablename__ = "ap_cron_job"

    class State:
        new = "new"
        disabled = "disabled"
        pending = "pending"
        running = "running"
        failed = "failed"
        finished = "finished"

    id = Column(Text, primary_key=True, default=make_uuid)

    name = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_run = Column(DateTime, nullable=True)
    schedule = Column(Text)
    actions = Column(Text)
    data: dict[str, Any] = Column(JSONB, nullable=False)  # type: ignore
    state = Column(Text, default=State.new)
    timeout = Column(Integer, default=cron_conf.get_job_timeout())

    def __str__(self):
        return (
            f"[Job id: {self.id}, name: {self.name} "
            f"actions: {self.actions}, schedule: {self.schedule}]"
        )

    @classmethod
    def get(cls, job_id: str) -> Self | None:
        query = model.Session.query(cls).filter(cls.id == job_id)

        return query.one_or_none()

    @classmethod
    def get_list(cls, states: Optional[list[str]] = None) -> list[Self]:
        """Get a list of cron jobs.

        Args:
            states (Optional[list[str]], optional): Filter by job state.
        """
        query = model.Session.query(cls)

        if states:
            query = query.filter(cls.state.in_(states))

        query = query.order_by(cls.last_run.desc())

        return query.all()

    def delete(self) -> None:
        model.Session().autoflush = False
        model.Session.delete(self)

    @classmethod
    def add(cls, job_data: CronJobData) -> DictizedCronJob:
        job = cls(
            name=job_data["name"],
            schedule=job_data["schedule"],
            actions=", ".join(job_data["actions"]),
            data={KWARGS: job_data["data"]},
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
            [action.strip() for action in self.actions.split(",")]
            if isinstance(self.actions, str)
            else self.actions
        )

    @property
    def kwargs(self):
        return self.data.get(KWARGS, {})
