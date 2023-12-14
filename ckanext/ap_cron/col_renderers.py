from __future__ import annotations

import ckan.plugins.toolkit as tk

from ckanext.toolbelt.decorators import Collector

import ckanext.ap_main.types as ap_types

renderer, get_renderers = Collector("ap_cron").split()


@renderer
def last_run(
    rows: ap_types.ItemList, row: ap_types.Item, value: ap_types.ItemValue, **kwargs
) -> str:
    date_format: str = kwargs.get("date_format", "%d/%m/%Y - %H:%M")

    if not value:
        return tk._("Never")

    return tk.h.render_datetime(value, date_format=date_format)


@renderer
def schedule(
    rows: ap_types.ItemList, row: ap_types.Item, value: ap_types.ItemValue, **kwargs
) -> str:
    tooltip = tk.h.ap_cron_explain_cron_schedule(value)

    return tk.render(
        "ap_cron/renderers/schedule.html",
        extra_vars={"value": value, "tooltip": tooltip},
    )


@renderer
def json_display(
    rows: ap_types.ItemList, row: ap_types.Item, value: ap_types.ItemValue, **kwargs
) -> str:
    return tk.render(
        "ap_cron/renderers/json.html",
        extra_vars={"value": value},
    )
