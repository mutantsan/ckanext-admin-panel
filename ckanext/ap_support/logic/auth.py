from __future__ import annotations

from ckan import types


def ap_support_ticket_search(
    context: types.Context, data_dict: types.DataDict
) -> types.AuthResult:
    return _sysadmin_only()


def _sysadmin_only() -> types.AuthResult:
    return {"success": False}
