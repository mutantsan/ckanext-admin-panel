from __future__ import annotations
from typing import Literal

from ckan.types import SignalMapping
import ckan.plugins as p
import ckan.plugins.toolkit as tk

import ckanext.ap_main.types as ap_types
from ckanext.ap_main.interfaces import IAdminPanel


@tk.blanket.config_declarations
@tk.blanket.blueprints
class AdminPanelExamplePlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
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
            tk.signals.ckanext.signal("ap_main:collect_config_pages"): [
                {
                    "sender": "Admin panel example",
                    "receiver": collect_example_pages_subscriber,
                },
            ],
        }


def collect_config_sections_subscriber(sender: None):
    return ["Admin panel example"]


def collect_example_pages_subscriber(sender: Literal["Admin panel example"]):
    return [
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
    ]
