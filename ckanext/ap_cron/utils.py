from __future__ import annotations

import logging
from typing import Any
from datetime import datetime as dt, timedelta as td

from croniter import croniter
from dateutil.parser import isoparse as parse_iso_date

import ckan.plugins.toolkit as tk
from ckan.lib.jobs import get_queue as get_jobs_queue

from ckanext.ap_cron import config as cron_conf
from ckanext.ap_cron import model as cron_model
from ckanext.ap_cron.const import LOG_NAME


log = logging.getLogger(LOG_NAME)


def get_next_run_datetime(date: dt, schedule: str) -> dt:
    """Get a datetime object of the next job run"""
    return croniter(schedule, date).get_next(dt)


def enqueue_cron_job(job_id: str) -> bool:
    cron_job = cron_model.CronJob.get(job_id)

    if not cron_job:
        log.exception("[id:%s] Unable to find a cron job", job_id)
        return False

    data = {
        "api_key": get_site_user_apitoken(),
        "job_type": "ap_cron_job",
        "result_url": get_job_callback_url(),
        "data": {
            "cron_job": cron_job,
            "actions": cron_job.get_actions,
            "kwargs": cron_job.data["kwargs"],
        },
    }

    try:
        tk.enqueue_job(
            cron_job_pipe, [data], rq_kwargs={"timeout": cron_conf.get_job_timeout()}
        )
    except Exception:
        log.exception("[id:%s] Unable to enqueued cron job", job_id)
        return False

    log.info("[id:%s] Cron job has been enququed", job_id)

    return True


def get_existing_task(cron_job: cron_model.CronJob) -> dict[str, Any] | None:
    """Check if the specified cron job is already in progress"""

    task_id = cron_job.data.get("task_id")

    if not task_id:
        return None

    try:
        existing_task = tk.get_action("task_status_show")(
            {"ignore_auth": True}, {"entity_id": task_id}
        )

    except tk.ObjectNotFound:
        return None

    return existing_task


def cron_job_pipe(data_dict: dict[str, Any]):
    """This function runs a list of actions for a specific cron job successively.
    The result of the action is passed to the next one."""

    job: cron_model.CronJob = data_dict["data"]["cron_job"]

    log.info("[id:%s] starting to piping a cron job", job.id)

    tk.get_action("ap_cron_update_cron_job")(
        {"ignore_auth": True},
        {
            "id": job.id,
            "state": cron_model.CronJob.State.running,
        },
    )

    for action in data_dict["data"]["actions"]:
        log.info("[id:%s] starting to run an action %s", job.id, action)

        try:
            data_dict = tk.get_action(action)({}, data_dict["data"]["kwargs"])
        except tk.ValidationError as e:
            job.data["errors"] = e.error_dict

            log.exception(
                "[id:%s] An action %s has failed. Terminating...", job.id, action
            )
            log.exception("[id:%s] Error dict %s", job.id, e.error_dict)

            return tk.get_action("ap_cron_update_cron_job")(
                {"ignore_auth": True},
                {
                    "id": job.id,
                    "state": cron_model.CronJob.State.failed,
                    "data": job.data,
                },
            )

        log.info("[id:%s] the action %s was executed successfully...", job.id, action)

    log.info("[id:%s] cron job has successfuly finished", job.id)

    tk.get_action("ap_cron_update_cron_job")(
        {"ignore_auth": True},
        {
            "id": job.id,
            "state": cron_model.CronJob.State.finished,
        },
    )


def get_job_callback_url() -> str:
    return tk.url_for("api.action", logic_function="cron_job_callback", qualified=True)


def get_site_user_apitoken() -> str:
    return tk.get_action("get_site_user")({"ignore_auth": True}, {})["apikey"]
