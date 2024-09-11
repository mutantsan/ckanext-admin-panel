from __future__ import annotations

import ckan.plugins.toolkit as tk


def ap_comma_separated_string(value: list[str]) -> str:
    if not isinstance(value, list):
        raise tk.Invalid("Value should be a string")

    return ", ".join(value)
