from __future__ import annotations

from ckan.plugins import toolkit as tk

from ckanext.toolbelt.decorators import Collector

import ckanext.ap_main.types as ap_types

renderer, get_renderers = Collector("ap").split()


@renderer
def date(
    rows: ap_types.ItemList, row: ap_types.Item, value: ap_types.ItemValue, **kwargs
) -> str:
    date_format: str = kwargs.get("date_format", "%d/%m/%Y - %H:%M")

    return tk.h.render_datetime(value, date_format=date_format)


@renderer
def text_render(
    rows: ap_types.ItemList, row: ap_types.Item, value: ap_types.ItemValue, **kwargs
) -> str:
    return str(value)


@renderer
def user_link(
    rows: ap_types.ItemList, row: ap_types.Item, value: ap_types.ItemValue, **kwargs
) -> str:
    return tk.h.linked_user(value, maxlength=kwargs.get("maxlength") or 20)


@renderer
def bool(rows: ap_types.ItemList, row: ap_types.Item, value: ap_types.ItemValue) -> str:
    return "Yes" if value else "No"


@renderer
def action_render(
    rows: ap_types.ItemList, row: ap_types.Item, value: ap_types.ItemValue, **kwargs
) -> str:
    ...


@renderer
def log_level(
    rows: ap_types.ItemList, row: ap_types.Item, value: ap_types.ItemValue, **kwargs
) -> str:
    return tk.h.ap_get_log_level_label(value)
