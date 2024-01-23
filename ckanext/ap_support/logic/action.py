from __future__ import annotations

from ckan.logic import validate
from ckan.plugins import toolkit as tk
from ckan import types

import ckanext.ap_support.logic.schema as schema
import ckanext.ap_support.model as support_model


@tk.side_effect_free
@validate(schema.ticket_search)
def ap_support_ticket_search(context: types.Context, data_dict: types.DataDict):
    tk.check_access("ap_support_ticket_search", context, data_dict)

    if data_dict.get("state"):
        result = support_model.Ticket.get_list(states=[data_dict["state"]])
    else:
        result = support_model.Ticket.get_list()

    return [job.dictize(context) for job in result]
