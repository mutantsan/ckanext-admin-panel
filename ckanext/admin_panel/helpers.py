from __future__ import annotations

from typing import Optional, TypedDict

import ckan.plugins.toolkit as tk
import ckan.lib.munge as munge


class SectionConfig(TypedDict):
    name: str
    configs: list["ConfigurationItem"]


class ConfigurationItem(TypedDict, total=False):
    name: str
    blueprint: str
    info: Optional[str]


def ap_get_config_sections() -> list[SectionConfig]:
    return [
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
                )
            ],
        ),
    ]


def ap_munge_string(value: str) -> str:
    return munge.munge_name(value)
