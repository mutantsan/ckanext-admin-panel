from __future__ import annotations

import ckan.plugins as p
import ckan.plugins.toolkit as tk

import ckanext.ap_main.types as ap_types
from ckanext.ap_main.interfaces import IAdminPanel

_renderers_cache: dict[str, ap_types.ColRenderer] = {}


def ap_before_request() -> None:
    try:
        tk.check_access(
            "admin_panel_access",
            {"user": tk.current_user.name},
        )
    except tk.NotAuthorized:
        tk.abort(403, tk._("Need to be system administrator to administer"))


def get_all_renderers() -> dict[str, ap_types.ColRenderer]:
    if not _renderers_cache:
        for plugin in reversed(list(p.PluginImplementations(IAdminPanel))):
            for name, fn in plugin.get_col_renderers().items():
                _renderers_cache[name] = fn

    return _renderers_cache
