from __future__ import annotations

import logging
from datetime import datetime

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
    return logging.getLevelName(value)


@renderer
def list(
    rows: ap_types.ItemList, row: ap_types.Item, value: ap_types.ItemValue, **kwargs
):
    return ", ".join(value)


@renderer
def day_passed(
    rows: ap_types.ItemList, row: ap_types.Item, value: ap_types.ItemValue, **kwargs
) -> str:
    if not value:
        return 0

    try:
        datetime_obj = datetime.fromisoformat(value)
    except AttributeError:
        return 0

    current_date = datetime.now()

    days_passed = (current_date - datetime_obj).days

    return tk.render(
        "admin_panel/renderers/day_passed.html",
        extra_vars={"value": days_passed},
    )
