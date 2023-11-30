from __future__ import annotations

from typing import Any

from croniter import croniter

import ckan.plugins.toolkit as tk
from ckan.logic import get_action
from ckan import types

from ckanext.ap_cron import model as cron_model


def cron_schedule_validator(value: str, context: types.Context) -> Any:
    """Ensures that the cron schedule has valid format"""
    result = croniter.is_valid(value)

    if value == "@reboot":
        result = True
    elif len(value.split()) == 6:
        # We don't support spring schedule format
        result = False
    else:
        result = croniter.is_valid(value)

    if not result:
        raise tk.Invalid(tk._("The cron schedule is not properly formed."))

    return value


def cron_job_exists(job_id: str, context: types.Context) -> Any:
    """Ensures that the cron job with a given id exists."""

    session = context["session"]

    if not session.query(cron_model.CronJob).get(job_id):
        raise tk.Invalid("The cron job not found.")

    return job_id


def cron_action_exists(actions: list[str], context: types.Context) -> Any:
    """Check if all the actions are registered in CKAN"""
    for action in actions:
        try:
            get_action(action)
        except KeyError as e:
            raise tk.Invalid(str(e))

    return actions
