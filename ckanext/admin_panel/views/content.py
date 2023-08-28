from __future__ import annotations

import logging
from functools import partial
from typing import Any, Callable, Optional, Union

from flask import Blueprint, Response
from flask.views import MethodView
from typing_extensions import TypeAlias

import ckan.lib.navl.dictization_functions as df
import ckan.logic as logic
import ckan.plugins.toolkit as tk
from ckan import model, types
from ckan.lib.helpers import Page

from ckanext.admin_panel.utils import ap_before_request

ContentList: TypeAlias = "list[dict[str, Any]]"

ap_content = Blueprint("ap_content", __name__, url_prefix="/admin-panel")
ap_content.before_request(ap_before_request)

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

        return result_pkgs + result_orgs + [grp for grp in result_groups]

    def post(self) -> Response:
        bulk_action = tk.request.form.get("bulk-action")
        content_ids = tk.request.form.getlist("entity_id")

        if not bulk_action or not content_ids:
            return tk.redirect_to("ap_content.list")

        action_func = self._get_bulk_action(bulk_action)

        if not action_func:
            tk.h.flash_error(tk._("The bulk action is not implemented"))
            return tk.redirect_to("ap_content.list")

        action_func(content_ids)

        tk.h.flash_success(tk._("Done."))

        return tk.redirect_to("ap_content.list")

    def _get_pager(self, content_list: ContentList) -> Page:
        page_number = tk.h.get_page_number(tk.request.args)
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
            tk.h.ap_table_column("creator_user_id", "Author", type_="user_link", width="10%"),
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
                "text": tk._("Purge selected entities(s)"),
            },
            {
                "value": "2",
                "text": tk._("Restore selected user(s)"),
            },
        ]

    def _get_bulk_action(self, value: str) -> Callable[[list[str]], None] | None:
        return {
            # "1": partial(self._change_user_role, is_sysadmin=True),
            # "2": partial(self._change_user_role, is_sysadmin=False),
            # "3": partial(self._change_user_state, is_active=False),
            # "4": partial(self._change_user_state, is_active=True),
        }.get(value)

    # @staticmethod
    # def _change_user_role(
    #     user_ids: list[str], is_sysadmin: Optional[bool] = False
    # ) -> None:
    #     for user_id in user_ids:
    #         try:
    #             logic.get_action("user_patch")(
    #                 {"ignore_auth": True}, {"id": user_id, "sysadmin": is_sysadmin}
    #             )
    #         except tk.ObjectNotFound:
    #             pass

    # @staticmethod
    # def _change_user_state(
    #     user_ids: list[str], is_active: Optional[bool] = False
    # ) -> None:
    #     state = model.State.ACTIVE if is_active else model.State.DELETED

    #     for user_id in user_ids:
    #         try:
    #             logic.get_action("user_patch")(
    #                 {"ignore_auth": True},
    #                 {"id": user_id, "state": state},
    #             )
    #         except tk.ObjectNotFound:
    #             pass

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


class ContentProxyView(MethodView):
    def get(self, view: str, entity_type: str, entity_id: str) -> Union[str, Response]:
        return tk.redirect_to(f"{entity_type}.{view}", id=entity_id)


ap_content.add_url_rule("/content/list", view_func=ContentListView.as_view("list"))
ap_content.add_url_rule(
    "/content/<view>/<entity_type>/<entity_id>",
    view_func=ContentProxyView.as_view("entity_proxy"),
)
