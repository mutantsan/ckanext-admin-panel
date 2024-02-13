from __future__ import annotations

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
