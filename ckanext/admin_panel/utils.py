from __future__ import annotations

from typing import cast


import ckan.model as model
import ckan.plugins.toolkit as tk
from ckan.types import Context


def ap_before_request() -> None:
    try:
        tk.check_access(
            "admin_panel_access",
            cast(
                Context,
                {
                    "model": model,
                    "user": tk.current_user.name,
                    "auth_user_obj": tk.current_user,
                },
            ),
        )
    except tk.NotAuthorized:
        tk.abort(403, tk._("Need to be system administrator to administer"))
