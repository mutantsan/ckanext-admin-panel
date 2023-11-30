from __future__ import annotations

from cron_descriptor import get_description

import ckan.plugins.toolkit as tk

from ckanext.toolbelt.decorators import Collector

from ckanext.ap_cron import config as cron_conf

helper, get_helpers = Collector("ap_cron").split()


@helper
def get_actions_list_options() -> list[dict[str, str]]:
    from ckan.logic import _actions

    return [
        {
            "value": action,
            "text": action,
        }
        for action in sorted(_actions)
    ]


@helper
def get_job_timeout() -> int:
    return cron_conf.get_job_timeout()


@helper
def explain_cron_schedule(schedule: str) -> str:
    non_standard = {
        "@reboot": tk._("At CKAN startup"),
        "@hourly": tk._("Every hour"),
        "@daily": tk._("Every day"),
        "@weekly": tk._("Every week"),
        "@monthly": tk._("Every month"),
        "@yearly": tk._("Every year"),
    }

    if explanation := non_standard.get(schedule):
        return explanation

    return get_description(schedule)
