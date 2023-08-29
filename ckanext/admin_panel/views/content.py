from __future__ import annotations

import logging
from functools import partial
from typing import Any, Callable, Optional, Union

from flask import Blueprint, Response
from flask.views import MethodView
from typing_extensions import TypeAlias

import ckan.logic as logic
import ckan.plugins.toolkit as tk
from ckan import model, types
from ckan.lib.helpers import Page

import ckanext.admin_panel.utils as ap_utils

ContentList: TypeAlias = "list[dict[str, Any]]"

ap_content = Blueprint("ap_content", __name__, url_prefix="/admin-panel")
ap_content.before_request(ap_utils.ap_before_request)

log = logging.getLogger(__name__)


class ContentListView(MethodView):
    def get(self) -> Union[str, Response]:
        self.q = tk.request.args.get("q", "").strip()
        self.order_by = tk.request.args.get("order_by", "name")
        self.sort = tk.request.args.get("sort", "desc")
        self.state = tk.request.args.get("state", "")
        self.type = tk.request.args.get("type", "")

        data_dict = {"q": self.q, "order_by": self.order_by}

        # TODO: write custom user_list action to make it more flexible
        self.content_list = self._fake_content_list()
        self.content_list = self._filter_by_state(self.content_list)
        self.content_list = self._filter_by_type(self.content_list)
        self.content_list = self._search_items(self.content_list)
        self.content_list = self._sort_items(self.content_list)

        return tk.render(
            "admin_panel/config/content/content_list.html", self._prepare_data_dict()
        )

    def _make_context(self) -> types.Context:
        return {
            "user": tk.current_user.name,
            "auth_user_obj": tk.current_user,
        }

    def _prepare_data_dict(self) -> dict[str, Any]:
        return {
            "page": self._get_pager(self.content_list),
            "columns": self._get_table_columns(),
            "q": self.q,
            "order_by": self.order_by,
            "sort": self.sort,
            "state": self.state,
            "type": self.type,
            "bulk_options": self._get_bulk_action_options(),
        }

    def _fake_content_list(self) -> list[dict[str, Any]]:
        result_pkgs = tk.get_action("package_search")(
            {"ignore_auth": True}, {"include_private": True}
        )["results"]

        result_orgs = tk.get_action("organization_list")(
            {"ignore_auth": True}, {"all_fields": True}
        )

        for org in result_orgs:
            org["metadata_created"] = org["created"]
            org["metadata_modified"] = org["created"]
            org["notes"] = org["description"]

        result_groups = tk.get_action("group_list")(
            {"ignore_auth": True}, {"all_fields": True}
        )

        for group in result_groups:
            group["metadata_created"] = group["created"]
            group["metadata_modified"] = group["created"]
            group["notes"] = group["description"]

        return (
            result_pkgs
            + get_deleted_datasets()
            + result_orgs
            + get_deleted_orgs()
            + result_groups
            + get_deleted_groups()
        )

    def post(self) -> Response:
        bulk_action = tk.request.form.get("bulk-action")
        content_ids_to_types = tk.request.form.getlist("entity_id")
        action_func = self._get_bulk_action(bulk_action) if bulk_action else None

        if not action_func:
            tk.h.flash_error(tk._("The bulk action is not implemented"))
            return tk.redirect_to("ap_content.list")

        for entity_type, entity_ids in self._group_entity_ids_by_types(
            content_ids_to_types
        ).items():
            if action_func(entity_ids, entity_type):
                tk.h.flash_success(tk._("Done."))

        return tk.redirect_to("ap_content.list")

    def _group_entity_ids_by_types(
        self, ids_to_types: list[str]
    ) -> dict[str, list[str]]:
        result = {}

        for row in ids_to_types:
            try:
                entity_id, entity_type = row.split("|")
            except ValueError:
                continue

            result.setdefault(entity_type, [])
            result[entity_type].append(entity_id)

        return result

    def _get_pager(self, content_list: ContentList) -> Page:
        page_number = tk.h.get_page_number(tk.request.args)
        # TODO add config
        limit: int = 20

        return Page(
            collection=content_list,
            page=page_number,
            url=tk.h.pager_url,
            item_count=len(content_list),
            items_per_page=limit,
        )

    def _get_table_columns(self) -> list[dict[str, Any]]:
        return [
            tk.h.ap_table_column("title", "Title", width="10%"),
            tk.h.ap_table_column("notes", "Notes", width="30%", sortable=False),
            tk.h.ap_table_column("type", "Type", width="10%", sortable=False),
            tk.h.ap_table_column(
                "creator_user_id", "Author", type_="user_link", width="10%"
            ),
            tk.h.ap_table_column("state", "State", width="10%"),
            tk.h.ap_table_column(
                "metadata_created", "Create at", type_="date", width="10%"
            ),
            tk.h.ap_table_column(
                "metadata_modified", "Modified at", type_="date", width="10%"
            ),
            tk.h.ap_table_column(
                "actions",
                type_="actions",
                width="10%",
                sortable=False,
                actions=[
                    tk.h.ap_table_action(
                        "ap_content.entity_proxy",
                        tk._("Edit"),
                        {"entity_id": "$id", "entity_type": "$type", "view": "edit"},
                    ),
                    tk.h.ap_table_action(
                        "ap_content.entity_proxy",
                        tk._("View"),
                        {"entity_id": "$id", "entity_type": "$type", "view": "read"},
                    ),
                ],
            ),
        ]

    def _get_bulk_action_options(self):
        return [
            {
                "value": "1",
                "text": tk._("Restore selected entities(s)"),
            },
            {
                "value": "2",
                "text": tk._("Delete selected entities(s)"),
            },
            {
                "value": "3",
                "text": tk._("Purge selected entities(s)"),
            },
        ]

    def _get_bulk_action(self, value: str) -> Callable[[list[str], str], bool] | None:
        return {
            "1": partial(self._change_entities_state, is_active=True),
            "2": partial(self._change_entities_state, is_active=False),
            "3": partial(self._purge_entities),
        }.get(value)

    @staticmethod
    def _change_entities_state(
        entity_ids: list[str], entity_type: str, is_active: Optional[bool] = False
    ) -> bool:
        state = model.State.ACTIVE if is_active else model.State.DELETED
        actions = {
            "dataset": "package_patch",
            "organization": "organization_patch",
            "group": "group_patch",
        }
        action = actions.get(entity_type)

        if not action:
            tk.h.flash_error(f"Changing {entity_type} entity state isn't supported")
            return False

        for entity_id in entity_ids:
            try:
                logic.get_action(action)(
                    {"ignore_auth": True},
                    {"id": entity_id, "state": state},
                )
            except tk.ObjectNotFound:
                pass

        return True

    @staticmethod
    def _purge_entities(entity_ids: list[str], entity_type: str) -> bool:
        actions = {
            "dataset": "dataset_purge",
            "organization": "organization_purge",
            "group": "group_purge",
        }
        action = actions.get(entity_type)

        if not action:
            tk.h.flash_error(f"Purging {entity_type} entity isn't supported")
            return False

        for entity_id in entity_ids:
            try:
                logic.get_action(action)(
                    {"ignore_auth": True},
                    {"id": entity_id},
                )
            except tk.ObjectNotFound:
                pass

        return True

    def _filter_by_state(self, content_list: ContentList) -> ContentList:
        if self.state == model.State.DELETED:
            return [
                user for user in content_list if user["state"] == model.State.DELETED
            ]

        if self.state == model.State.ACTIVE:
            return [
                user for user in content_list if user["state"] == model.State.ACTIVE
            ]

        return content_list

    def _filter_by_type(self, content_list: ContentList) -> ContentList:
        if not self.type:
            return content_list

        return [entity for entity in content_list if entity["type"] == self.type]

    def _search_items(self, content_list: ContentList) -> ContentList:
        if not self.q:
            return content_list

        return [
            entity
            for entity in content_list
            if self.q.lower() in entity["title"].lower()
            or self.q.lower() in entity["notes"].lower()
        ]

    def _sort_items(self, content_list: ContentList) -> ContentList:
        self.order_by = tk.request.args.get("order_by", "modified_at")
        self.sort = tk.request.args.get("sort", "desc")

        return sorted(
            content_list,
            key=lambda x: x.get(self.order_by, ""),
            reverse=self.sort == "desc",
        )


def get_deleted_datasets() -> list[dict[str, Any]]:
    """Return a list of deleted datasets, either from DB or from search index"""
    return (
        _get_deleted_datasets_from_db()
        if tk.config["ckan.search.remove_deleted_packages"]
        else _get_deleted_datasets_from_search_index()
    )


def _get_deleted_datasets_from_db() -> list[dict[str, Any]]:
    return [
        package.as_dict()
        for package in model.Session.query(model.Package)
        .filter_by(state=model.State.DELETED)
        .all()
    ]


def _get_deleted_datasets_from_search_index() -> list[dict[str, Any]]:
    results = tk.get_action("package_search")(
        {"ignore_auth": True},
        {
            "fq": "+state:deleted",
            "include_private": True,
        },
    )

    return results["results"]


def get_deleted_orgs() -> list[dict[str, Any]]:
    return [
        org.as_dict()
        for org in model.Session.query(model.Group)
        .filter_by(state=model.State.DELETED, is_organization=True)
        .all()
    ]


def get_deleted_groups() -> list[dict[str, Any]]:
    return [
        group.as_dict()
        for group in model.Session.query(model.Group).filter_by(
            state=model.State.DELETED, is_organization=False
        )
    ]


class ContentProxyView(MethodView):
    def get(self, view: str, entity_type: str, entity_id: str) -> Union[str, Response]:
        return tk.redirect_to(f"{entity_type}.{view}", id=entity_id)


ap_content.add_url_rule("/content/list", view_func=ContentListView.as_view("list"))
ap_content.add_url_rule(
    "/content/<view>/<entity_type>/<entity_id>",
    view_func=ContentProxyView.as_view("entity_proxy"),
)
