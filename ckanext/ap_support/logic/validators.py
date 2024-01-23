from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan import types

from ckanext.ap_support.model import Ticket


def ticket_id_exists(ticket_id: str, context: types.Context) -> Any:
    """Ensures that the cron job with a given id exists."""

    session = context["session"]

    if not session.query(Ticket).get(ticket_id):
        raise tk.Invalid("Ticket not found")

    return ticket_id
