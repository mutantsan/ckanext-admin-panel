from __future__ import annotations

from urllib.parse import urlencode

import ckan.plugins.toolkit as tk
import ckan.lib.munge as munge
import ckan.plugins as p

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
