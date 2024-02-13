from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Callable

from ckan.plugins import toolkit as tk
from ckanext.collection.types import BaseSerializer

from ckanext.toolbelt.decorators import Collector

from ckanext.ap_main.types import ColRenderer

renderer: Collector[ColRenderer]
get_renderers: Callable[[], dict[str, ColRenderer]]
renderer, get_renderers = Collector().split()


@renderer
def date(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    date_format: str = options.get("date_format", "%d/%m/%Y - %H:%M")

    return tk.h.render_datetime(value, date_format=date_format)


@renderer
def user_link(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    if not value:
        return ""
    return tk.h.linked_user(value, maxlength=options.get("maxlength") or 20)


@renderer
def bool(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    return "Yes" if value else "No"


@renderer
def log_level(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    return logging.getLevelName(value)


@renderer
def list(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
):
    return ", ".join(value)


@renderer
def none_as_empty(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> Any:
    return value if value is not None else ""


@renderer
def day_passed(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    if not value:
        return "0"

    try:
        datetime_obj = datetime.fromisoformat(value)
    except AttributeError:
        return "0"

    current_date = datetime.now()

    days_passed = (current_date - datetime_obj).days

    return tk.literal(tk.render(
        "admin_panel/renderers/day_passed.html",
        extra_vars={"value": days_passed},
    ))
