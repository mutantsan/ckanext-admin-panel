from __future__ import annotations

from typing import Any, Callable

import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckanext.collection.interfaces import ICollection, CollectionFactory
import ckanext.ap_main.types as ap_types
from ckanext.ap_main import helpers, collection
from ckanext.ap_main.col_renderers import get_renderers
from ckanext.ap_main.interfaces import IAdminPanel


@tk.blanket.blueprints
@tk.blanket.actions
@tk.blanket.auth_functions
class AdminPanelPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IBlueprint)
    p.implements(p.ITemplateHelpers)
    p.implements(IAdminPanel, inherit=True)
    p.implements(ICollection, inherit=True)

    # IConfigurer

    def update_config(self, config_: tk.CKANConfig):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "admin_panel")

    # ITemplateHelpers

    def get_helpers(self) -> dict[str, Callable[..., Any]]:
        return helpers.get_helpers()

    # IAdminPanel

    def get_col_renderers(self) -> dict[str, ap_types.ColRenderer]:
        return get_renderers()

    # ICollection
    def get_collection_factories(self) -> dict[str, CollectionFactory]:
        return {
            "ap-content": collection.ContentCollection,
            "ap-user": collection.UserCollection,
            "ap-logs": collection.DbLogCollection,
        }
