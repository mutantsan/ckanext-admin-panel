from __future__ import annotations

import ckan.plugins as p
import ckan.plugins.toolkit as tk

import ckanext.ap_main.types as ap_types
from ckanext.ap_main.interfaces import IAdminPanel
from ckanext.ap_main.types import ColRenderer

from ckanext.ap_support.col_renderers import get_renderers


@tk.blanket.blueprints
@tk.blanket.actions
@tk.blanket.auth_functions
@tk.blanket.validators
@tk.blanket.helpers
class AdminPanelSupportPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(IAdminPanel, inherit=True)

    # IConfigurer

    def update_config(self, config_: tk.CKANConfig):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "ap_cron")

    # IAdminPanel

    def register_config_sections(
        self, config_list: list[ap_types.SectionConfig]
    ) -> list[ap_types.SectionConfig]:
        config_list.append(
            ap_types.SectionConfig(
                name="Support system",
                configs=[
                    ap_types.ConfigurationItem(
                        name="Global settings",
                        blueprint="ap_user.list",
                        info="Support system configuration",
                    ),
                    ap_types.ConfigurationItem(
                        name="Dashboard",
                        blueprint="ap_support.list",
                        info="Support dashboard",
                    ),
                ],
            )
        )
        return config_list

    def get_col_renderers(self) -> dict[str, ColRenderer]:
        return get_renderers()
