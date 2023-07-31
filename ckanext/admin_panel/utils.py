from __future__ import annotations


import ckan.plugins.toolkit as tk


def ap_before_request() -> None:
    try:
        tk.check_access(
            "admin_panel_access",
            {"user": tk.current_user.name},
        )
    except tk.NotAuthorized:
        tk.abort(403, tk._("Need to be system administrator to administer"))
