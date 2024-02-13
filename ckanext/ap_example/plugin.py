from __future__ import annotations
from typing import Literal

from os import path

from yaml import safe_load

import ckan.plugins as p
import ckan.plugins.toolkit as tk
import ckan.logic as logic
from ckan.config.declaration import Declaration, Key
from ckan.types import SignalMapping

import ckanext.ap_main.types as ap_types


@tk.blanket.blueprints
class AdminPanelExamplePlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IConfigDeclaration, inherit=True)
    p.implements(p.ISignal)

    # IConfigurer

    def update_config(self, config_: tk.CKANConfig):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "ap_test")

    # ISignal

    def get_signal_subscriptions(self) -> SignalMapping:
        return {
            tk.signals.ckanext.signal("ap_main:collect_config_sections"): [
                collect_config_sections_subscriber,
            ],
        }

    # IConfigDeclaration

    def declare_config_options(self, declaration: Declaration, key: Key):
        logic.clear_validators_cache()

        with open(path.dirname(__file__) + "/config_declaration.yaml") as file:
            data_dict = safe_load(file)

        return declaration.load_dict(data_dict)


def collect_config_sections_subscriber(sender: None):
    return ap_types.SectionConfig(
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
