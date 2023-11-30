from __future__ import annotations

from typing import cast
from datetime import datetime as dt

from ckan.logic import validate
from ckan.plugins import toolkit as tk


import ckanext.ap_cron.logic.schema as cron_schema
from ckanext.ap_cron.model import CronJob
from ckanext.ap_cron.utils import enqueue_cron_job


@tk.side_effect_free
@validate(cron_schema.add_cron_job)
def ap_cron_add_cron_job(context, data_dict):
    tk.check_access("ap_cron_add_job", context, data_dict)

    return CronJob.add(data_dict)


@tk.side_effect_free
@validate(cron_schema.get_cron_job)
def ap_cron_get_cron_job(context, data_dict):
    tk.check_access("ap_cron_get_job", context, data_dict)

    return cast(CronJob, CronJob.get(data_dict["id"])).dictize(context)


@tk.side_effect_free
@validate(cron_schema.remove_cron_job)
def ap_cron_remove_cron_job(context, data_dict):
    tk.check_access("ap_cron_remove_job", context, data_dict)

    job = cast(CronJob, CronJob.get(data_dict["id"]))
    job.delete()

    context["session"].commit()

    return True


@tk.side_effect_free
@validate(cron_schema.get_cron_job_list)
def ap_cron_get_cron_job_list(context, data_dict):
    tk.check_access("ap_cron_get_job_list", context, data_dict)

    if data_dict.get("state"):
        return CronJob.get_list(data_dict["state"])

    return CronJob.get_list()


@tk.side_effect_free
@validate(cron_schema.update_cron_job)
def ap_cron_update_cron_job(context, data_dict):
    tk.check_access("ap_cron_update_job", context, data_dict)

    job = cast(CronJob, CronJob.get(data_dict["id"]))

    for key, value in data_dict.items():
        setattr(job, key, value)

    job.last_run = dt.utcnow()

    context["session"].commit()

    return job.dictize(context)


@tk.side_effect_free
@validate(cron_schema.run_cron_job)
def ap_cron_run_cron_job(context, data_dict):
    tk.check_access("ap_cron_update_job", context, data_dict)

    job = cast(CronJob, CronJob.get(data_dict["id"]))

    if job.state == CronJob.State.running:
        raise tk.ValidationError({"message": tk._("The cron job is already running.")})

    return {
        "job": job.dictize(context),
        "success": enqueue_cron_job(job.id),

    }


def cron_job_callback(context, data_dict):
    """Update cron job task state. This action is typically called whenever the status of a job changes."""

    import ipdb

    ipdb.set_trace()
    pass
    # metadata, status = _get_or_bust(data_dict, ["metadata", "status"])

    # res_id = _get_or_bust(metadata, "resource_id")

    # # Pass metadata, not data_dict, as it contains the resource id needed
    # # on the auth checks
    # p.toolkit.check_access("xloader_submit", context, metadata)

    # task = p.toolkit.get_action("task_status_show")(
    #     context, {"entity_id": res_id, "task_type": "xloader", "key": "xloader"}
    # )

    # task["state"] = status
    # task["last_updated"] = str(datetime.datetime.utcnow())
    # task["error"] = data_dict.get("error")

    # resubmit = False

    # if status in ("complete", "running_but_viewable"):
    #     # Create default views for resource if necessary (only the ones that
    #     # require data to be in the DataStore)
    #     resource_dict = p.toolkit.get_action("resource_show")(context, {"id": res_id})

    #     dataset_dict = p.toolkit.get_action("package_show")(
    #         context, {"id": resource_dict["package_id"]}
    #     )

    #     for plugin in p.PluginImplementations(xloader_interfaces.IXloader):
    #         plugin.after_upload(context, resource_dict, dataset_dict)

    #     p.toolkit.get_action("resource_create_default_resource_views")(
    #         context,
    #         {
    #             "resource": resource_dict,
    #             "package": dataset_dict,
    #             "create_datastore_views": True,
    #         },
    #     )

    #     # Check if the uploaded file has been modified in the meantime
    #     if resource_dict.get("last_modified") and metadata.get("task_created"):
    #         try:
    #             last_modified_datetime = parse_date(resource_dict["last_modified"])
    #             task_created_datetime = parse_date(metadata["task_created"])
    #             if last_modified_datetime > task_created_datetime:
    #                 log.debug(
    #                     "Uploaded file more recent: %s > %s",
    #                     last_modified_datetime,
    #                     task_created_datetime,
    #                 )
    #                 resubmit = True
    #         except ValueError:
    #             pass
    #     # Check if the URL of the file has been modified in the meantime
    #     elif (
    #         resource_dict.get("url")
    #         and metadata.get("original_url")
    #         and resource_dict["url"] != metadata["original_url"]
    #     ):
    #         log.debug(
    #             "URLs are different: %s != %s",
    #             resource_dict["url"],
    #             metadata["original_url"],
    #         )
    #         resubmit = True

    # context["ignore_auth"] = True
    # p.toolkit.get_action("task_status_update")(context, task)

    # if resubmit:
    #     log.debug(
    #         "Resource %s has been modified, " "resubmitting to DataPusher", res_id
    #     )
    #     p.toolkit.get_action("xloader_submit")(context, {"resource_id": res_id})


def aaa_test_cron(context, data_dict):
    from time import sleep

    print("We are inside a test bg func, waitin for a 5 sec")
    print(data_dict)
    sleep(5)
    print("Done with waiting")
