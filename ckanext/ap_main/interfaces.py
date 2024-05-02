from __future__ import annotations

from typing import Any

from ckan.plugins.interfaces import Interface

import ckanext.ap_main.types as ap_types


class IAdminPanel(Interface):
    def register_toolbar_button(
        self, toolbar_buttons_list: list[ap_types.ToolbarButton]
    ) -> list[ap_types.ToolbarButton]:
        """Extension will receive the list of toolbar button objects."""
        return toolbar_buttons_list

    def get_col_renderers(self) -> dict[str, ap_types.ColRenderer]:
        """Allows an extension to register its own col renderers

        Return a dictionary mapping renderes names (strings) to renderer
        fucntions. For example::

            {'col_counter': col_counter}

        """
        return {}

    def before_config_update(self, schema_id: str, data: dict[str, Any]) -> None:
        """Called before configuration update"""
        pass

    def after_config_update(
        self, schema_id: str, data_before_update: dict[str, Any], data: dict[str, Any]
    ) -> None:
        """Called after configuration update"""
        pass
