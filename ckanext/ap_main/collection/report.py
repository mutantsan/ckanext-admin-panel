from __future__ import annotations

from typing import Any, Iterable, Sequence
import sqlalchemy as sa

from ckan import model
from ckanext.collection.types import (
    InputFilter,
    LinkFilter,
    SelectFilter,
    Filter,
    SelectOption,
)
from ckanext.collection.utils import Filters, ModelData

from ckanext.ap_main.model import ApLogs

from .base import ApCollection, MultiSelectFilter


class DbLogCollection(ApCollection[Any]):
    ColumnsFactory = ApCollection.ColumnsFactory.with_attributes(
        names=[
            "name",
            "path",
            "level",
            "timestamp",
            "message",
        ],
        sortable={
            "name",
            "path",
            "level",
            "timestamp",
        },
        searchable={"message"},
        labels={
            "name": "Name",
            "path": "Path",
            "level": "Level",
            "timestamp": "Timestamp",
            "message": "Message",
        },
        serializers={
            "level": [("log_level", {})],
            "timestamp": [("date", {})],
        },
    )

    DataFactory = ModelData.with_attributes(
        use_naive_filters=True,
        use_naive_search=True,
        is_scalar=True,
        model=ApLogs,
    )

    class FiltersFactory(Filters["DbLogCollection"]):
        def make_filters(self) -> Sequence[Filter[Any]]:
            log_type_options: Iterable[SelectOption] = [
                {"value": v, "text": v}
                for v in model.Session.scalars(sa.select(sa.distinct(ApLogs.name)))
            ]

            return [
                InputFilter(
                    name="q",
                    type="input",
                    options={
                        "label": "Search",
                        "placeholder": "Search",
                    },
                ),
                MultiSelectFilter(
                    name="level",
                    type="multiselect",
                    options={
                        "label": "Level",
                        "options": [
                            {"value": str(ApLogs.Level.NOTSET), "text": "NOTSET"},
                            {"value": str(ApLogs.Level.DEBUG), "text": "DEBUG"},
                            {"value": str(ApLogs.Level.INFO), "text": "INFO"},
                            {"value": str(ApLogs.Level.WARNING), "text": "WARNING"},
                            {"value": str(ApLogs.Level.ERROR), "text": "ERROR"},
                            {"value": str(ApLogs.Level.CRITICAL), "text": "CRITICAL"},
                        ],
                    },
                ),
                MultiSelectFilter(
                    name="name",
                    type="multiselect",
                    options={
                        "label": "Type",
                        "options": log_type_options,
                    },
                ),
                LinkFilter(
                    name="type",
                    type="link",
                    options={
                        "label": "Clear",
                        "endpoint": "ap_report.logs",
                        "kwargs": {},
                    },
                ),
            ]
