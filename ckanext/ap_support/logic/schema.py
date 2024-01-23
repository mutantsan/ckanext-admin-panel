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
    return {
        "status": [ignore_missing, unicode_safe, one_of(STATUSES)]
    }
