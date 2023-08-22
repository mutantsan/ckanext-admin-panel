from __future__ import annotations

from urllib.parse import urlencode
from typing import Any, Optional

import ckan.plugins.toolkit as tk
import ckan.lib.munge as munge
import ckan.plugins as p
import ckan.model as model

import ckanext.admin_panel.model as ap_model
from ckanext.admin_panel.types import SectionConfig, ConfigurationItem
from ckanext.admin_panel.interfaces import IAdminPanel


def ap_get_config_sections() -> list[SectionConfig]:
    default_sections = [
        SectionConfig(
            name=tk._("Basic site settings"),
            configs=[
                ConfigurationItem(
                    name=tk._("CKAN configuration"),
                    info=tk._("CKAN site config options"),
                    blueprint=(
                        "ap_basic.editable_config"
                        if p.plugin_loaded("editable_config")
                        else "ap_basic.config"
                    ),
                ),
                ConfigurationItem(
                    name=tk._("Trash bin"),
                    info=tk._("Purge deleted entities"),
                    blueprint="ap_basic.trash",
                ),
            ],
        ),
        SectionConfig(
            name=tk._("Schema engine config"),
            configs=[
                ConfigurationItem(
                    name=tk._("SOLR config"),
                    info=tk._("SOLR configuration options"),
                    blueprint="ap_basic.config",
                )
            ],
        ),
        SectionConfig(
            name=tk._("User settings"),
            configs=[
                ConfigurationItem(
                    name=tk._("User permissions"),
                    blueprint="user.index",
                ),
                ConfigurationItem(
                    name=tk._("User permissions"),
                    blueprint="user.index",
                ),
            ],
        ),
    ]

    for plugin in reversed(list(p.PluginImplementations(IAdminPanel))):
        default_sections = plugin.register_config_sections(default_sections)

    return default_sections


def ap_munge_string(value: str) -> str:
    return munge.munge_name(value)


def ap_add_url_param(key: str, value: str) -> str:
    """Add a GET param to URL."""
    blueprint, view = p.toolkit.get_endpoint()

    url = tk.h.url_for(f"{blueprint}.{view}")

    params_items = tk.request.args.items(multi=False)
    params = [(k, v) for k, v in params_items if k != "page" and k != key]
    params.append((key, value))

    return (
        url
        + "?"
        + urlencode(
            [
                (k, v.encode("utf-8") if isinstance(v, str) else str(v))
                for k, v in params
            ]
        )
    )


def ap_user_list_state_options() -> list[dict[str, str]]:
    return [
        {"value": "any", "text": "Any"},
        {"value": model.State.DELETED, "text": "Deleted"},
        {"value": model.State.ACTIVE, "text": "Active"},
    ]


def ap_user_list_role_options() -> list[dict[str, str]]:
    return [
        {"value": "any", "text": "Any"},
        {"value": "sysadmin", "text": "Sysadmin"},
        {"value": "user", "text": "User"},
    ]


def ap_table_column(
    name: str,
    label: Optional[str] = None,
    sortable: Optional[bool] = True,
    type_: Optional[str] = "text",
    width: Optional[str] = "fit-content",
    actions: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    supported_types = ("text", "bool", "date", "user_link", "actions")

    if type_ not in supported_types:
        raise tk.ValidationError("Column type {type_} is not supported")

    return {
        "name": name,
        "label": label or name.title(),
        "sortable": sortable,
        "type": type_,
        "width": width,
        "actions": actions,
    }


def ap_log_list_type_options() -> list[dict[str, str | int]]:
    return [
        {"value": log_name, "text": log_name}
        for log_name in sorted({log["name"] for log in ap_model.ApLogs.all()})
    ]


def ap_log_list_level_options() -> list[dict[str, str | int]]:
    return [
        {"value": ap_model.ApLogs.Level.NOTSET, "text": "NOTSET"},
        {"value": ap_model.ApLogs.Level.DEBUG, "text": "DEBUG"},
        {"value": ap_model.ApLogs.Level.INFO, "text": "INFO"},
        {"value": ap_model.ApLogs.Level.WARNING, "text": "WARNING"},
        {"value": ap_model.ApLogs.Level.ERROR, "text": "ERROR"},
        {"value": ap_model.ApLogs.Level.ERROR, "text": "CRITICAL"},
    ]
