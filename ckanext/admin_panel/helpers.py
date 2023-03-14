import ckan.plugins.toolkit as tk
import ckan.lib.munge as munge


def ap_get_config_sections():
    return [
        {
            "name": tk._("Basic site settings"),
            "configs": [
                {
                    "name": tk._("Basic config"),
                    "info": tk._("Default CKAN site config options"),
                    "blueprint": "ap_basic.config",
                },
                {
                    "name": tk._("Pagination settings"),
                    "blueprint": "ap_basic.config",
                },
            ],
        },
        {
            "name": tk._("Schema engine config"),
            "configs": [
                {
                    "name": tk._("SOLR config"),
                    "info": tk._("SOLR configuration options"),
                    "blueprint": "ap_basic.config",
                }
            ],
        },
        {
            "name": tk._("User settings"),
            "configs": [
                {
                    "name": tk._("User permissions"),
                    "blueprint": "ap_basic.config",
                }
            ],
        },
    ]


def ap_munge_string(value: str) -> str:
    return munge.munge_name(value)
