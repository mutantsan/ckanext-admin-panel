from __future__ import annotations

from typing import Any, Dict

from ckan.logic.schema import validator_args

Schema = Dict[str, Any]


@validator_args
def ap_doi_get_packages_doi(unicode_safe, default) -> Schema:
    return {
        "doi_status": [default(""), unicode_safe],
        "q": [default(""), unicode_safe],
    }
