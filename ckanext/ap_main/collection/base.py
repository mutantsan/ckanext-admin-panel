from __future__ import annotations
from typing import Any, Sequence

from typing_extensions import NotRequired, TypedDict
from ckanext.collection.types import (
    BaseSerializer,
    TData,
    TDataCollection,
    ValueSerializer,
    Filter,
)
import ckan.plugins.toolkit as tk
from ckanext.collection.utils import HtmxTableSerializer, Collection

from ckanext.collection.shared import configurable_attribute


def default_value_serializers(serializer: BaseSerializer) -> dict[str, ValueSerializer]:
    return {
        "date": lambda value, options, name, record, self: tk.h.render_datetime(
            value, date_format=options.get("date_format", "%d/%m/%Y - %H:%M")
        ),
        "user_link": lambda value, options, name, record, self: tk.h.linked_user(
            value, maxlength=options.get("maxlength") or 20
        )
        if value
        else "",
    }


class ApHtmxTableSerializer(HtmxTableSerializer[TDataCollection]):
    base_class: str = configurable_attribute("ap-collection")

    ensure_dictized = configurable_attribute(True)

    main_template: str = configurable_attribute(
        "collection/serialize/ap_htmx_table/main.html",
    )
    record_template: str = configurable_attribute(
        "collection/serialize/ap_htmx_table/record.html",
    )
    form_template: str = configurable_attribute(
        "collection/serialize/ap_htmx_table/form.html",
    )
    action_template: str = configurable_attribute(
        "collection/serialize/ap_htmx_table/action.html",
    )
    value_serializers = configurable_attribute(
        default_factory=default_value_serializers
    )


class ApCollection(Collection[TData]):
    SerializerFactory = ApHtmxTableSerializer


class BulkActionOptions(TypedDict):
    label: str
    options: Sequence[dict[str, Any]]


class RowActionOptions(TypedDict):
    endpoint: str
    label: str
    params: dict[str, Any]
    icon: NotRequired[str]


RowAction = Filter[RowActionOptions]
BulkAction = Filter[BulkActionOptions]
