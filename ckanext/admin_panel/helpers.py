from __future__ import annotations

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
                    name=tk._("Basic config"),
                    info=tk._("Default CKAN site config options"),
                    blueprint="ap_basic.config",
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
