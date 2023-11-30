from __future__ import annotations

from ckan import types


def ap_cron_add_job(
    context: types.Context, data_dict: types.DataDict
) -> types.AuthResult:
    return _sysadmin_only()


def ap_cron_get_job(
    context: types.Context, data_dict: types.DataDict
) -> types.AuthResult:
    return _sysadmin_only()


def ap_cron_remove_job(
    context: types.Context, data_dict: types.DataDict
) -> types.AuthResult:
    return _sysadmin_only()


def ap_cron_update_job(
    context: types.Context, data_dict: types.DataDict
) -> types.AuthResult:
    return _sysadmin_only()


def ap_cron_get_job_list(
    context: types.Context, data_dict: types.DataDict
) -> types.AuthResult:
    return _sysadmin_only()


def _sysadmin_only() -> types.AuthResult:
    return {"success": False}
