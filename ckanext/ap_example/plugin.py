from __future__ import annotations

import ckan.plugins as p
import ckan.plugins.toolkit as tk

import ckanext.ap_main.types as ap_types
from ckanext.ap_main.interfaces import IAdminPanel


@tk.blanket.config_declarations
@tk.blanket.blueprints
class AdminPanelExamplePlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(IAdminPanel, inherit=True)

    # IConfigurer

    def update_config(self, config_: tk.CKANConfig):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "ap_test")

    # IAdminPanel

    def register_config_sections(
        self, config_list: list[ap_types.SectionConfig]
    ) -> list[ap_types.SectionConfig]:
        config_list.append(
            ap_types.SectionConfig(
                name="Admin panel example",
                configs=[
                    ap_types.ConfigurationItem(
                        name="Example settings",
                        blueprint="ap_example.config",
                        info="An example of schema-generated configuration form",
                    ),
                    ap_types.ConfigurationItem(
                        name="Example display",
                        blueprint="ap_example.display",
                        info="Example of displaying values submitted from a form",
                    ),
                ],
            )
        )
        return config_list
