from __future__ import annotations

import ckan.plugins.toolkit as tk

CONFIG_SHOW_TB_SEARCH = "ckanext.admin_panel.show_toolbar_search"
DEFAULT_SHOW_TB_SEARCH = True


CONFIG_SHOW_TB_THEME_SWITCHER = "ckanext.admin_panel.show_toolbar_theme_switcher"
DEFAULT_SHOW_TB_THEME_SWITCHER = True


def show_toolbar_search() -> bool:
    return tk.asbool(tk.config.get(CONFIG_SHOW_TB_SEARCH, DEFAULT_SHOW_TB_SEARCH))


def show_toolbar_theme_switcher() -> bool:
    return tk.asbool(
        tk.config.get(CONFIG_SHOW_TB_THEME_SWITCHER, DEFAULT_SHOW_TB_THEME_SWITCHER)
    )
