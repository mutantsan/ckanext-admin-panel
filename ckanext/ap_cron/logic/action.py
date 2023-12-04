from __future__ import annotations

import logging
from typing import cast
from datetime import datetime as dt

from ckan.logic import validate
from ckan.plugins import toolkit as tk


import ckanext.ap_cron.logic.schema as cron_schema
from ckanext.ap_cron.model import CronJob
from ckanext.ap_cron.utils import enqueue_cron_job
from ckanext.ap_cron.const import LOG_NAME

log = logging.getLogger(LOG_NAME)


@validate(cron_schema.add_cron_job)
def ap_cron_add_cron_job(context, data_dict):
    tk.check_access("ap_cron_add_job", context, data_dict)

    job = CronJob.add(data_dict)

    log.info("[id:%s] Cron job has been created")

    return job


@tk.side_effect_free
@validate(cron_schema.get_cron_job)
def ap_cron_get_cron_job(context, data_dict):
    tk.check_access("ap_cron_get_job", context, data_dict)

    return cast(CronJob, CronJob.get(data_dict["id"])).dictize(context)


@validate(cron_schema.remove_cron_job)
def ap_cron_remove_cron_job(context, data_dict):
    tk.check_access("ap_cron_remove_job", context, data_dict)

    job = cast(CronJob, CronJob.get(data_dict["id"]))
    job.delete()

    context["session"].commit()

    log.info("[id:%s] Cron job has been removed", job.id)

    return True


@tk.side_effect_free
@validate(cron_schema.get_cron_job_list)
def ap_cron_get_cron_job_list(context, data_dict):
    tk.check_access("ap_cron_get_job_list", context, data_dict)

    if data_dict.get("state"):
        return CronJob.get_list(data_dict["state"])

    return CronJob.get_list()


@validate(cron_schema.update_cron_job)
def ap_cron_update_cron_job(context, data_dict):
    tk.check_access("ap_cron_update_job", context, data_dict)

    job = cast(CronJob, CronJob.get(data_dict["id"]))

    for key, value in data_dict.items():
        setattr(job, key, value)

    job.last_run = dt.utcnow()  # type: ignore

    context["session"].commit()

    log.info("[id:%s] Cron job has been updated: %s", job.id, data_dict)

    return job.dictize(context)


@validate(cron_schema.run_cron_job)
def ap_cron_run_cron_job(context, data_dict):
    tk.check_access("ap_cron_update_job", context, data_dict)

    job = cast(CronJob, CronJob.get(data_dict["id"]))

    if tk.h.ap_cron_is_job_running(job.dictize({})):
        log.exception("[id:%s] The cron job is already running.", job.id)
        raise tk.ValidationError({"message": tk._("The cron job is already running.")})

    return {
        "job": job.dictize(context),
        "success": enqueue_cron_job(job.id),
    }


def cron_job_callback(context, data_dict):
    """Update cron job task state. This action is typically called whenever the status of a job changes."""

    import ipdb

    ipdb.set_trace()
    # TODO


def aaa_test_cron(context, data_dict):
    from time import sleep

    sleep(15)
