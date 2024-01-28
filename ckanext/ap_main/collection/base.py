from __future__ import annotations

from typing import Any, Literal, Sequence

from typing_extensions import NotRequired, TypedDict

import ckan.plugins.toolkit as tk

from ckanext.collection.shared import configurable_attribute
from ckanext.collection.types import (
    BaseSerializer,
    Filter,
    TData,
    TDataCollection,
    ValueSerializer,
)
from ckanext.collection.utils import Collection, HtmxTableSerializer, Columns

import ckanext.ap_cron.col_renderers as cron_renderers


def default_value_serializers(serializer: BaseSerializer) -> dict[str, ValueSerializer]:
    """Value serializers available for all collections.

    These functions serves the same purpose as renderers in original
    implementation. When signature of renderers changed to ValueSerializer,
    this function can be replaced with `get_all_renderers`.
    """

    return {
        "date": lambda value, options, name, record, self: tk.h.render_datetime(
            value, date_format=options.get("date_format", "%d/%m/%Y - %H:%M")
        ),
        "user_link": lambda value, options, name, record, self: tk.h.linked_user(
            value, maxlength=options.get("maxlength") or 20
        )
        if value
        else "",
        "schedule": lambda value, options, name, record, self: tk.literal(
            cron_renderers.schedule([], record, value, **options)
        ),
        "last_run": lambda value, options, name, record, self: tk.literal(
            cron_renderers.last_run([], record, value, **options)
        ),
        "json_display": lambda value, options, name, record, self: tk.literal(
            cron_renderers.json_display([], record, value, **options)
        ),
    }


class ApColumns(Columns[TDataCollection]):
    width = configurable_attribute(default_factory=lambda self: {})


class ApHtmxTableSerializer(HtmxTableSerializer[TDataCollection]):
    """Main table serializer.

    For now it just customizes standard HtmxTableSerializer. No new attributes,
    no new functions.

    Because `ensure_dictized` flag enabled, all records inside
    `record_template` are available as dictionaries. This is done intentionaly,
    for compatibility with CKAN v2.11. Here's an example of change in logic:

    >>> record = model.Session.query(User.id, User.name).first()
    >>> # v2.10
    >>> id, name = record.id, record.name
    >>>
    >>> # v2.11
    >>> id, name = record[0], record[1]

    When you query separate columns of the model, you are no longer allowed to
    access columns by their original name. Now you have to use index of the
    column instead. Such restriction will certainly decrease readability of
    templates, so we are using `ensure_dictized` to convert each record into a
    dictionary with all original column names available.

    """

    base_class: str = configurable_attribute("ap-collection")

    ensure_dictized = configurable_attribute(True)
    push_url = True

    main_template: str = configurable_attribute(
        "collection/serialize/ap_htmx_table/main.html",
    )

    table_template: str = configurable_attribute(
        "collection/serialize/ap_htmx_table/table.html",
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

    # TODO: replace with `get_all_renderers` after signature update
    value_serializers = configurable_attribute(
        default_factory=default_value_serializers
    )



class ApCollection(Collection[TData]):
    SerializerFactory = ApHtmxTableSerializer

    ColumnsFactory = ApColumns


class BulkActionOptions(TypedDict):
    """Options of the bulk_action filter."""

    label: str
    options: Sequence[dict[str, Any]]


class RowActionOptions(TypedDict):
    """Options of the row_action filter."""

    endpoint: str
    label: str
    params: dict[str, Any]
    icon: NotRequired[str]


class RowAction(Filter[RowActionOptions]):
    type: Literal["row_action"]


class BulkAction(Filter[BulkActionOptions]):
    type: Literal["bulk_action"]
