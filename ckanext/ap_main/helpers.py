from __future__ import annotations

from typing import Any, Optional
from urllib.parse import urlencode

import ckan.lib.munge as munge
import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckanext.toolbelt.decorators import Collector

import ckanext.ap_main.config as ap_config
import ckanext.ap_main.utils as ap_utils
from ckanext.ap_main.interfaces import IAdminPanel
from ckanext.ap_main.types import ConfigurationItem, SectionConfig, ToolbarButton

helper, get_helpers = Collector("ap").split()


@helper
def get_config_sections() -> list[SectionConfig]:
    """Prepare a config section structure for render"""
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
                )
            ],
        ),
    ]

    for plugin in reversed(list(p.PluginImplementations(IAdminPanel))):
        default_sections = plugin.register_config_sections(default_sections)

    return default_sections


@helper
def get_toolbar_structure() -> list[ToolbarButton]:
    configuration_subitems = [
        ToolbarButton(
            label=section["name"],
            subitems=[
                ToolbarButton(
                    label=config_item["name"], url=tk.url_for(config_item["blueprint"])
                )
                for config_item in section["configs"]
            ],
        )
        for section in get_config_sections()
    ]

    default_structure = [
        ToolbarButton(
            label=tk._("Content"),
            icon="fa fa-folder",
            url=tk.url_for("ap_content.list"),
        ),
        # ToolbarButton(
        #     label=tk._("Appearance"),
        #     icon="fa fa-wand-magic-sparkles",
        # ),
        # ToolbarButton(
        #     label=tk._("Extensions"),
        #     icon="fa fa-gem",
        #     url=tk.url_for(
        #         "api.action", ver=3, logic_function="status_show", qualified=True
        #     ),
        # ),
        ToolbarButton(
            label=tk._("Configuration"),
            icon="fa fa-gear",
            url=tk.url_for("ap_config_list.index"),
            subitems=configuration_subitems,
        ),
        ToolbarButton(
            label=tk._("Users"),
            icon="fa fa-user-friends",
            url=tk.url_for("ap_user.list"),
            subitems=[
                ToolbarButton(
                    label=tk._("Add user"),
                    url=tk.url_for("ap_user.create"),
                    icon="fa fa-user-plus",
                )
            ],
        ),
        ToolbarButton(
            label=tk._("Reports"),
            icon="fa fa-chart-bar",
            subitems=[
                # ToolbarButton(label=tk._("Available updates")),
                ToolbarButton(
                    label=tk._("Recent log messages"),
                    url=tk.url_for("ap_report.logs"),
                )
            ],
        ),
        # ToolbarButton(label=tk._("Help"), icon="fa fa-circle-info"),
        ToolbarButton(
            icon="fa fa-gavel",
            url=tk.url_for("admin.index"),
            attributes={"title": tk._("Old admin")},
        ),
        ToolbarButton(
            label=tk.h.user_image((tk.current_user.name), size=22),
            url=tk.url_for("user.read", id=tk.current_user.name),
            attributes={"title": tk._("View profile")},
        ),
        ToolbarButton(
            icon="fa fa-tachometer",
            url=tk.url_for("dashboard.datasets"),
            attributes={"title": tk._("View dashboard")},
        ),
        ToolbarButton(
            icon="fa fa-cog",
            url=tk.url_for("user.edit", id=tk.current_user.name),
            attributes={"title": tk._("Profile settings")},
        ),
        ToolbarButton(
            icon="fa fa-sign-out",
            url=tk.url_for("user.logout"),
            attributes={"title": tk._("Log out")},
        ),
    ]

    for plugin in reversed(list(p.PluginImplementations(IAdminPanel))):
        default_structure = plugin.register_toolbar_button(default_structure)

    return default_structure


@helper
def munge_string(value: str) -> str:
    return munge.munge_name(value)


@helper
def add_url_param(key: str, value: str) -> str:
    """Add a GET param to URL."""
    blueprint, view = p.toolkit.get_endpoint()

    url = tk.h.url_for(f"{blueprint}.{view}")

    params_items = tk.request.args.items(multi=True)
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


# TODO: remove after updating mailcraft
@helper
def table_column(
    name: str,
    label: Optional[str] = None,
    sortable: Optional[bool] = True,
    width: Optional[str] = "fit-content",
    actions: Optional[list[dict[str, Any]]] = None,
    column_renderer: Optional[str] = "ap_text_render",
    renderer_kwargs: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Create a structure for a sorted table column item.

    Args:
        name: A column name will be used as a sorting GET param.
        label (optional): A human-readable column label. Defaults to None.
        sortable (optional): add column sort. Defaults to True.
        column_renderer (optional): defines how column will be rendered. Defaults to "ap_text".
        width (optional): width of the column. Defaults to "fit-content".
        actions (optional): A list of actions. Defaults to None.
    """
    col_renderers = ap_utils.get_all_renderers()

    if column_renderer not in col_renderers:
        raise tk.ValidationError(f"Column renderer {column_renderer} is not supported")

    return {
        "name": name,
        "label": label or name.title(),
        "sortable": sortable,
        "width": width,
        "actions": actions,
        "column_renderer": col_renderers[column_renderer],
        "renderer_kwargs": renderer_kwargs or {},
    }


# TODO: remove after updating mailcraft
@helper
def table_action(
    endpoint: str,
    label: Optional[str] = None,
    icon: Optional[str] = None,
    params: Optional[dict[str, str]] = None,
    attributes: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """Create a structure for a sorted table action item.

    Params must be a dict, where key is a field name and value could be a arbitrary
    value or an attribute of a table row item. To refer the actual attribute,ap_def
    use $ sign at the beggining of the value. E.g.

    ap_action("user.edit", tk._("Edit"), {"id": "$name"})

    Args:
        endpoint: an endpoint to build an action URL
        label: label for a button text
        params (optional): params dict. Defaults to None.
        attributes (optional): attributes dict. Defaults to None.
    """
    return {
        "endpoint": endpoint,
        "label": label,
        "icon": icon,
        "params": params or {},
        "attributes": attributes or {},
    }


@helper
def show_toolbar_search() -> bool:
    return ap_config.show_toolbar_search()


@helper
def show_toolbar_theme_switcher() -> bool:
    return ap_config.show_toolbar_theme_switcher()


@helper
def user_add_role_options() -> list[dict[str, str | int]]:
    """Return a list of options for a user add form"""
    return [
        {"value": "user", "text": "Regular user"},
        {"value": "sysadmin", "text": "Sysadmin"},
    ]


@helper
def generate_page_unique_class() -> str:
    """Build a unique css class for each page"""

    return tk.h.ap_munge_string((f"ap-{tk.request.endpoint}"))


@helper
def get_arbitrary_schema(schema_id: str) -> dict[Any, Any] | None:
    """This is a temporary code. We've created a PR #403 to ckanext-scheming
    to support an arbitrary schemas. For now, we are creating a polyfill"""
    from ckanext.scheming.plugins import _load_schemas, _expand_schemas

    SCHEMA_OPTION = "scheming.arbitrary_schemas"
    SCHEMA_TYPE_FIELD = "schema_id"

    schema_urls = tk.config.get(SCHEMA_OPTION, "").split()
    schemas = _load_schemas(schema_urls, SCHEMA_TYPE_FIELD)

    expanded_schemas = _expand_schemas(schemas)

    return expanded_schemas.get(schema_id)
