from __future__ import annotations

from typing import Any, Dict

from ckan.logic.schema import validator_args

from ckanext.ap_support.model import Ticket

Schema = Dict[str, Any]
STATUSES = [
    Ticket.Status.opened,
    Ticket.Status.closed,
]


@validator_args
def ticket_search(ignore_missing, unicode_safe, one_of) -> Schema:
    return {"status": [ignore_missing, unicode_safe, one_of(STATUSES)]}


@validator_args
def ticket_create(not_missing, unicode_safe, user_id_or_name_exists) -> Schema:
    return {
        "subject": [not_missing, unicode_safe],
        "text": [not_missing, unicode_safe],
        "author_id": [not_missing, unicode_safe, user_id_or_name_exists],
    }


@validator_args
def ticket_show(ignore_missing, unicode_safe, ticket_id_exists) -> Schema:
    return {"id": [ignore_missing, unicode_safe, ticket_id_exists]}
