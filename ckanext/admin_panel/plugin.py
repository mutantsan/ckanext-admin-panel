from __future__ import annotations

from typing import Callable, Any

import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckanext.admin_panel import helpers


@tk.blanket.blueprints
@tk.blanket.actions
@tk.blanket.auth_functions
class AdminPanelPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IBlueprint)
    p.implements(p.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_: tk.CKANConfig):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "admin_panel")

    # ITemplateHelpers

    def get_helpers(self) -> dict[str, Callable[..., Any]]:
        return helpers.get_helpers()
