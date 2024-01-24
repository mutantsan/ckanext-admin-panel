from __future__ import annotations

from ckan import types


def ap_support_ticket_search(
    context: types.Context, data_dict: types.DataDict
) -> types.AuthResult:
    return _sysadmin_only()


def ap_support_ticket_delete(
    context: types.Context, data_dict: types.DataDict
) -> types.AuthResult:
    return _sysadmin_only()


def ap_support_ticket_create(
    context: types.Context, data_dict: types.DataDict
) -> types.AuthResult:
    return {"success": True}


def _sysadmin_only() -> types.AuthResult:
    return {"success": False}
