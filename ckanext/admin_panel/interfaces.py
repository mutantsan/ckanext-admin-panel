from __future__ import annotations

from ckan.plugins.interfaces import Interface

from ckanext.admin_panel.types import SectionConfig, ToolbarButton


class IAdminPanel(Interface):
    def register_config_sections(
        self, config_list: list[SectionConfig]
    ) -> list[SectionConfig]:
        """Extension will receive the list of section config objects."""
        return config_list

    def register_toolbar_button(
        self, toolbar_buttons_list: list[ToolbarButton]
    ) -> list[ToolbarButton]:
        """Extension will receive the list of toolbar button objects."""
        return toolbar_buttons_list
