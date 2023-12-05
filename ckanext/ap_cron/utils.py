from __future__ import annotations

import logging
from typing import Any, Optional
from datetime import datetime as dt

from croniter import croniter

import ckan.plugins.toolkit as tk

from ckanext.ap_cron.model import CronJob
from ckanext.ap_cron.const import LOG_NAME, ERRORS, KWARGS
from ckanext.ap_cron.types import DictizedCronJob

log = logging.getLogger(LOG_NAME)


def get_next_run_datetime(date: dt, schedule: str) -> dt:
    """Get a datetime object of the next job run"""
    return croniter(schedule, date).get_next(dt)


def enqueue_cron_job(job: CronJob) -> bool:
    if not job:
        log.exception("[id:%s] Unable to find a cron job", job.id)
        return False

    # throw away old errors on a new run
    job.data.pop(ERRORS, None)

    _update_job_state(job.id, CronJob.State.pending, job.data)

    log.info("[id:%s] The job %s has been added to the queue", job.id, job)

    try:
        tk.enqueue_job(
            cron_job_pipe,
            [
                {
                    "job_type": "ap_cron_job",
                    "data": {
                        "cron_job": job,
                        "actions": job.get_actions,
                        "kwargs": job.data.get(KWARGS, {}),
                    },
                }
            ],
            rq_kwargs={
                "timeout": job.timeout,
                "on_failure": job_failure_callback,
            },
        )
    except Exception:
        log.exception("[id:%s] Unable to enqueued cron job", job.id)
        return False

    log.info("[id:%s] Cron job has been enququed", job.id)

    return True


def job_failure_callback(rq_job, connection, type, value, traceback):
    """Mark a cron job as failed if the rq throw an exception"""
    job: CronJob = rq_job.args[0]["data"]["cron_job"]
    job.data[ERRORS] = str(value)

    _update_job_state(job.id, CronJob.State.failed, job.data)


def cron_job_pipe(data_dict: dict[str, Any]) -> DictizedCronJob:
    """This function runs a list of actions for a specific cron job successively.
    The result of the action is passed to the next one."""

    job: CronJob = data_dict["data"]["cron_job"]

    log.info("[id:%s] the cron job has been started", job.id)

    _update_job_state(job.id, CronJob.State.running)

    for action in data_dict["data"]["actions"]:
        log.info("[id:%s] starting to run an action %s", job.id, action)

        try:
            data_dict = tk.get_action(action)({}, data_dict["data"].get(KWARGS, {}))
        except tk.ValidationError as e:
            job.data[ERRORS] = e.error_dict

            log.exception(
                "[id:%s] An action %s has failed. Terminating...", job.id, action
            )
            log.exception("[id:%s] Error dict %s", job.id, e.error_dict)

            return _update_job_state(job.id, CronJob.State.failed, job.data)

        log.info("[id:%s] the action %s was executed successfully...", job.id, action)

    log.info("[id:%s] cron job has successfuly finished", job.id)

    return _update_job_state(job.id, CronJob.State.finished, job.data)


def _update_job_state(
    job_id: str, state: str, data: Optional[dict[str, Any]] = None
) -> DictizedCronJob:
    payload: dict[str, Any] = {
        "id": job_id,
        "state": state,
    }

    if data is not None:
        payload["data"] = data

    return tk.get_action("ap_cron_update_cron_job")({"ignore_auth": True}, payload)
