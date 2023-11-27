from __future__ import annotations

from ckanext.toolbelt.decorators import Collector


helper, get_helpers = Collector("ap_core").split()


@helper
def get_actions_list_options() -> list[dict[str, str]]:
    from ckan.logic import _actions
    return [{
        "value": action,
        "text": action,
    } for action in _actions]
