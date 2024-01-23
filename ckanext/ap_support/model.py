from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Column, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship, backref
from typing_extensions import Self

import ckan.model as model
from ckan.plugins import toolkit as tk

from ckanext.ap_support.types import DictizedTicket, TicketData

log = logging.getLogger(__name__)


class Ticket(tk.BaseModel):
    __tablename__ = "ap_support_ticket"

    class Status:
        opened = "opened"
        closed = "closed"

    id = Column(Integer, primary_key=True)
    subject = Column(Text)
    status = Column(Text, default=Status.opened)
    text = Column(Text)
    category = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    author_id: Optional[str] = Column(
        Text, ForeignKey(model.User.id), nullable=False
    )

    author = relationship(
        model.User,
        backref=backref("tickets", cascade="all, delete"),
    )

    def __str__(self):
        return f"Ticket #{self.id}: {self.subject}"

    @classmethod
    def get(cls, job_id: str) -> Self | None:
        query = model.Session.query(cls).filter(cls.id == job_id)

        return query.one_or_none()

    @classmethod
    def get_list(cls, statuses: Optional[list[str]] = None) -> list[Self]:
        """Get a list of cron jobs.

        Args:
            states (Optional[list[str]], optional): Filter by job state.
        """
        query = model.Session.query(cls)

        if statuses:
            query = query.filter(cls.status.in_(statuses))

        query = query.order_by(cls.updated_at.desc())

        return query.all()

    def delete(self) -> None:
        model.Session().autoflush = False
        model.Session.delete(self)

    @classmethod
    def add(cls, ticket_data: TicketData) -> DictizedTicket:
        ticket = cls(
            subject=ticket_data["subject"],
            text=ticket_data["text"],
            author=ticket_data["author_id"],
        )

        model.Session.add(ticket)
        model.Session.commit()

        return ticket.dictize({})

    def dictize(self, context) -> DictizedTicket:
        return {
            "id": self.id,
            "subject": self.subject,
            "status": self.status,
            "text": self.text,
            "author": self.author.as_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
