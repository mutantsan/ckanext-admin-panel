from __future__ import annotations

from typing import Any

from ckanext.ap_support import config as support_config


def ap_support_get_category_options() -> list[dict[str, Any]]:
    return [
        {"value": category, "text": category}
        for category in support_config.get_ticket_categories()
    ]
