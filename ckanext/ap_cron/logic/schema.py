from __future__ import annotations

from typing import Any, Dict

from ckan.logic.schema import validator_args

from ckanext.ap_cron import config as cron_conf
from ckanext.ap_cron.model import CronJob


Schema = Dict[str, Any]
STATES = [
    CronJob.State.new,
    CronJob.State.disabled,
    CronJob.State.pending,
    CronJob.State.running,
    CronJob.State.failed,
    CronJob.State.finished,
]


@validator_args
def add_cron_job(
    not_missing,
    default,
    unicode_safe,
    convert_to_json_if_string,
    dict_only,
    cron_schedule_validator,
    int_validator,
    is_positive_integer,
    json_list_or_string,
    list_of_strings,
    ignore,
    cron_action_exists,
    one_of,
) -> Schema:
    return {
        "name": [not_missing, unicode_safe],
        "schedule": [not_missing, unicode_safe, cron_schedule_validator],
        "actions": [
            not_missing,
            unicode_safe,
            json_list_or_string,
            list_of_strings,
            cron_action_exists,
        ],
        "timeout": [
            default(cron_conf.get_job_timeout()),
            int_validator,
            is_positive_integer,
        ],
        "data": [not_missing, convert_to_json_if_string, dict_only],
        "state": [default(CronJob.State.new), unicode_safe, one_of(STATES)],
    }


@validator_args
def get_cron_job(not_missing, unicode_safe, cron_job_exists) -> Schema:
    return {"id": [not_missing, unicode_safe, cron_job_exists]}


@validator_args
def remove_cron_job(not_missing, unicode_safe, cron_job_exists) -> Schema:
    return {"id": [not_missing, unicode_safe, cron_job_exists]}


@validator_args
def get_cron_job_list(ignore_missing, unicode_safe, one_of) -> Schema:
    return {"state": [ignore_missing, unicode_safe, one_of(STATES)]}


@validator_args
def run_cron_job(not_missing, unicode_safe, cron_job_exists) -> Schema:
    return {"id": [not_missing, unicode_safe, cron_job_exists]}


@validator_args
def update_cron_job(
    not_missing,
    ignore_missing,
    cron_job_exists,
    unicode_safe,
    convert_to_json_if_string,
    dict_only,
    cron_schedule_validator,
    int_validator,
    is_positive_integer,
    json_list_or_string,
    cron_actions_to_string,
    ignore,
    one_of,
) -> Schema:
    return {
        "id": [not_missing, unicode_safe, cron_job_exists],
        "name": [ignore_missing, unicode_safe],
        "schedule": [ignore_missing, unicode_safe, cron_schedule_validator],
        "actions": [ignore_missing, unicode_safe, json_list_or_string, cron_actions_to_string],
        "timeout": [
            ignore_missing,
            int_validator,
            is_positive_integer,
        ],
        "data": [ignore_missing, convert_to_json_if_string, dict_only],
        "state": [ignore_missing, unicode_safe, one_of(STATES)],
        "__extras": [ignore],
        "__junk": [ignore],
    }
