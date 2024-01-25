from __future__ import annotations

from typing import Any

from dominate import tags

import ckan.plugins.toolkit as tk
from ckan import model

from ckanext.collection.types import InputFilter, LinkFilter, SelectFilter
from ckanext.collection.utils import Columns, Filters, ModelData

from ckanext.ap_main.collection.base import (
    ApCollection,
    BulkAction,
    RowAction,
    ApHtmxTableSerializer,
)

from ckanext.ap_cron.model import CronJob


class CronCollection(ApCollection[Any]):
    SerializerFactory = ApHtmxTableSerializer.with_attributes(
        record_template="ap_cron/cron_record.html"
    )

    ColumnsFactory = Columns.with_attributes(
        names=[
            "bulk-action",
            "name",
            "actions",
            "data",
            "schedule",
            "updated_at",
            "last_run",
            "state",
            "row_actions",
        ],
        sortable={"name", "updated_at", "last_run", "state"},
        searchable={"name"},
        labels={
            "bulk-action": tk.literal(
                tags.input_(
                    type="checkbox",
                    name="bulk_check",
                    id="bulk_check",
                    data_module="ap-bulk-check",
                    data_module_selector='input[name="entity_id"]',
                )
            ),
            "name": "Name",
            "actions": "Actions",
            "data": "Data",
            "schedule": "schedule",
            "updated_at": "Updated At",
            "last_run": "Last run",
            "state": "State",
            "row_actions": "Actions",
        },
        width={
            "data": "30%",
            "row_actions": "15%",
        },
        serializers={
            "data": [("ap_cron_json_display", {})],
            "schedule": [("schedule", {})],
            "updated_at": [("date", {})],
            "last_run": [("last_run", {})],
        },
    )

    DataFactory = ModelData.with_attributes(
        model=CronJob,
        use_naive_filters=True,
        use_naive_search=True,
    )

    FiltersFactory = Filters.with_attributes(
        static_actions=[
            BulkAction(
                name="bulk-action",
                type="bulk_action",
                options={
                    "label": "Action",
                    "options": [
                        {"value": "1", "text": "Restore selected entities(s)"},
                        {"value": "2", "text": "Delete selected entities(s)"},
                        {"value": "3", "text": "Purge selected entities(s)"},
                    ],
                },
            ),
            RowAction(
                name="edit",
                type="row_action",
                options={
                    "endpoint": "home.about",
                    "label": "Edit",
                    "params": {},
                },
            ),
        ],
        static_filters=[
            InputFilter(
                name="q",
                type="input",
                options={
                    "label": "Search",
                    "placeholder": "Search",
                },
            ),
            SelectFilter(
                name="state",
                type="select",
                options={
                    "label": "State",
                    "options": [
                        {"value": "", "text": "Any"},
                        {"value": model.State.DELETED, "text": "Deleted"},
                        {"value": model.State.ACTIVE, "text": "Active"},
                    ],
                },
            ),
            SelectFilter(
                name="type",
                type="select",
                options={
                    "label": "Type",
                    "options": [
                        {"value": "", "text": "Any"},
                        {"value": "dataset", "text": "Dataset"},
                        {"value": "group", "text": "Group"},
                        {"value": "organization", "text": "Organization"},
                    ],
                },
            ),
            LinkFilter(
                name="type",
                type="link",
                options={
                    "label": "Clear",
                    "endpoint": "ap_content.list",
                    "kwargs": {},
                },
            ),
        ],
    )
