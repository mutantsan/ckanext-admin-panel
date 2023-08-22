from __future__ import annotations
from functools import partial

from typing import Any, Union, Callable, Optional
from typing_extensions import TypeAlias

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
import ckan.logic as logic
import ckan.lib.navl.dictization_functions as df
import ckan.logic.schema as schema
from ckan import types, model
from ckan.lib.helpers import Page

from ckanext.admin_panel.utils import ap_before_request
from ckanext.admin_panel.helpers import (
    ap_table_column as ap_column,
    ap_table_action as ap_action
)


UserList: TypeAlias = "list[dict[str, Any]]"

ap_user = Blueprint("ap_user", __name__, url_prefix="/admin-panel")
ap_user.before_request(ap_before_request)


class UserListView(MethodView):
    def get(self) -> Union[str, Response]:
        self.q = tk.request.args.get("q", "").strip()
        self.order_by = tk.request.args.get("order_by", "name")
        self.sort = tk.request.args.get("sort", "desc")
        self.state = tk.request.args.get("state", "")
        self.role = tk.request.args.get("role", "")

        data_dict = {"q": self.q, "order_by": self.order_by}

        try:
            logic.check_access("user_list", self._make_context(), data_dict)
        except logic.NotAuthorized:
            tk.abort(403, tk._("Not authorized to see this page"))

        # TODO: write custom user_list action to make it more flexible
        self.user_list = logic.get_action("user_list")(self._make_context(), data_dict)
        self.user_list = self._filter_by_state(self.user_list)
        self.user_list = self._filter_by_role(self.user_list)

        return tk.render(
            "admin_panel/config/user/user_list.html", self._prepare_data_dict()
        )

    def _make_context(self) -> types.Context:
        return {
            "user": tk.current_user.name,
            "auth_user_obj": tk.current_user,
        }

    def _prepare_data_dict(self) -> dict[str, Any]:
        user_list = self.user_list if self.sort == "desc" else self.user_list[::-1]

        return {
            "page": self._get_pager(user_list),
            "columns": self._get_table_columns(),
            "q": self.q,
            "order_by": self.order_by,
            "sort": self.sort,
            "state": self.state,
            "role": self.role,
            "bulk_options": self._get_bulk_action_options(),
        }

    def post(self) -> Response:
        bulk_action = tk.request.form.get("bulk-action")
        user_ids = tk.request.form.getlist("entity_id")

        if not bulk_action or not user_ids:
            return tk.redirect_to("ap_user.list")

        action_func = self._get_bulk_action(bulk_action)

        if not action_func:
            tk.h.flash_error(tk._("The bulk action is not implemented"))
            return tk.redirect_to("ap_user.list")

        action_func(user_ids)

        tk.h.flash_success(tk._("Done."))

        return tk.redirect_to("ap_user.list")

    def _get_pager(self, users_list: UserList) -> Page:
        page_number = tk.h.get_page_number(tk.request.args)
        limit: int = tk.config.get("ckan.user_list_limit")

        return Page(
            collection=users_list,
            page=page_number,
            url=tk.h.pager_url,
            item_count=len(users_list),
            items_per_page=limit,
        )

    def _get_table_columns(self) -> list[dict[str, Any]]:
        return [
            ap_column("name", "Username", type_="user_link", width="23%"),
            ap_column("display_name", "Full Name", width="25%"),
            ap_column("email", "Email", width="20%"),
            ap_column("state", "State", width="10%"),
            ap_column("sysadmin", "Sysadmin", type_="bool", width="10%"),
            ap_column(
                "actions",
                sortable=False,
                type_="actions",
                width="10%",
                actions=[
                    ap_action("user.edit", tk._("Edit"), {"id": "$name"}),
                ],
            ),
        ]

    def _get_bulk_action_options(self):
        return [
            {
                "value": "1",
                "text": tk._("Add the sysadmin role to the selected user(s)"),
            },
            {
                "value": "2",
                "text": tk._("Remove the sysadmin role from the selected user(s)"),
            },
            {
                "value": "3",
                "text": tk._("Block the selected user(s)"),
            },
            {"value": "4", "text": tk._("Unblock the selected user(s)")},
        ]

    def _get_bulk_action(self, value: str) -> Callable[[list[str]], None] | None:
        return {
            "1": partial(self._change_user_role, is_sysadmin=True),
            "2": partial(self._change_user_role, is_sysadmin=False),
            "3": partial(self._change_user_state, is_active=False),
            "4": partial(self._change_user_state, is_active=True),
        }.get(value)

    @staticmethod
    def _change_user_role(
        user_ids: list[str], is_sysadmin: Optional[bool] = False
    ) -> None:
        for user_id in user_ids:
            try:
                logic.get_action("user_patch")(
                    {"ignore_auth": True}, {"id": user_id, "sysadmin": is_sysadmin}
                )
            except tk.ObjectNotFound:
                pass

    @staticmethod
    def _change_user_state(
        user_ids: list[str], is_active: Optional[bool] = False
    ) -> None:
        state = model.State.ACTIVE if is_active else model.State.DELETED

        for user_id in user_ids:
            try:
                logic.get_action("user_patch")(
                    {"ignore_auth": True},
                    {"id": user_id, "state": state},
                )
            except tk.ObjectNotFound:
                pass

    def _filter_by_state(self, users_list: UserList) -> UserList:
        if self.state == model.State.DELETED:
            return [user for user in users_list if user["state"] == model.State.DELETED]

        if self.state == model.State.ACTIVE:
            return [user for user in users_list if user["state"] == model.State.ACTIVE]

        return users_list

    def _filter_by_role(self, users_list: UserList) -> UserList:
        if self.role == "sysadmin":
            return [user for user in users_list if user["sysadmin"]]
        elif self.role == "user":
            return [user for user in users_list if not user["sysadmin"]]
        return users_list


class UserAddView(MethodView):
    def get(
        self,
        data: Optional[dict[str, Any]] = None,
        errors: Optional[dict[str, Any]] = None,
        error_summary: Optional[dict[str, Any]] = None,
    ) -> str:
        return tk.render(
            "admin_panel/config/user/create_form.html",
            extra_vars={
                "data": data or {},
                "errors": errors or {},
                "error_summary": error_summary or {},
            },
        )

    def post(self) -> str | Response:
        context = self._make_context()

        try:
            data_dict = self._parse_payload()
        except df.DataError:
            tk.abort(400, tk._("Integrity Error"))

        try:
            user_dict = logic.get_action("user_create")(context, data_dict)
        except logic.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.get(data_dict, errors, error_summary)

        link = (
            tk.h.literal(f"<a href='{tk.url_for('user.read', id=user_dict['name'])}'>")
            + "testuser_1"
            + tk.h.literal("</a>")
        )
        tk.h.flash_success(
            tk._(f"Created a new user account for {link}"), allow_html=True
        )

        return tk.redirect_to("ap_user.create")

    def _make_context(self) -> types.Context:
        context: types.Context = {
            "user": tk.current_user.name,
            "auth_user_obj": tk.current_user,
            "schema": schema.user_new_form_schema(),
            "save": "save" in tk.request.form,
        }

        return context

    def _parse_payload(self) -> dict[str, Any]:
        data_dict = logic.clean_dict(
            df.unflatten(logic.tuplize_dict(logic.parse_params(tk.request.form)))
        )

        data_dict.update(
            logic.clean_dict(
                df.unflatten(logic.tuplize_dict(logic.parse_params(tk.request.files)))
            )
        )

        return data_dict


ap_user.add_url_rule("/user/list", view_func=UserListView.as_view("list"))
ap_user.add_url_rule("/user/add", view_func=UserAddView.as_view("create"))
