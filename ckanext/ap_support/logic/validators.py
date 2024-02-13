from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan import types

import ckanext.ap_support.config as support_config
from ckanext.ap_support.model import Ticket


def ticket_id_exists(ticket_id: str, context: types.Context) -> Any:
    """Ensures that the ticket with a given id exists."""

    session = context["session"]

    if not session.query(Ticket).get(ticket_id):
        raise tk.Invalid("Ticket not found")

    return ticket_id


def ap_support_category_validator(ticket_category: str) -> str:
    allowed_categories = support_config.get_ticket_categories()

    if ticket_category not in allowed_categories:
        raise tk.Invalid(f"Category {ticket_category} is not allowed")

    return ticket_category
