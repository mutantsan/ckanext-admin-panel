from __future__ import annotations

import ckan.plugins.toolkit as tk

import ckanext.ap_main.types as ap_types
from ckanext.toolbelt.decorators import Collector

renderer, get_renderers = Collector("ap_support").split()


@renderer
def status(
    rows: ap_types.ItemList, row: ap_types.Item, value: ap_types.ItemValue, **kwargs
) -> str:
    return tk.render(
        "ap_support/renderers/status.html",
        extra_vars={"value": value},
    )


@renderer
def user_link(
    rows: ap_types.ItemList, row: ap_types.Item, value: ap_types.ItemValue, **kwargs
) -> str:
    return tk.h.linked_user(value["id"], maxlength=kwargs.get("maxlength") or 20)
