from __future__ import annotations

from typing import Any, TypedDict


class TicketData(TypedDict):
    subject: str
    text: str
    author_id: str
    category: str


class DictizedTicket(TypedDict):
    id: int
    subject: str
    status: str
    text: str
    author: dict[str, Any]
    created_at: str
    updated_at: str
