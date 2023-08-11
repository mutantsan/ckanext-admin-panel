from __future__ import annotations

from typing import Any, Union

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
import ckan.logic as logic
from ckan import types
from ckan.types.logic import action_result as action_types
from ckan.lib.helpers import Page

from ckanext.admin_panel.utils import ap_before_request


ap_user = Blueprint("ap_user", __name__, url_prefix="/admin-panel")
ap_user.before_request(ap_before_request)


class UserList(MethodView):
    def get(self) -> Union[str, Response]:
        q = tk.request.args.get("q", "")
        order_by = tk.request.args.get("order_by", "name")
        sort = tk.request.args.get("sort", "desc")
        state = tk.request.args.get("state", "")
        role = tk.request.args.get("role", "")

        context: types.Context = {
            "user": tk.current_user.name,
            "auth_user_obj": tk.current_user,
        }

        data_dict = {"q": q, "order_by": order_by}

        try:
            logic.check_access("user_list", context, data_dict)
        except logic.NotAuthorized:
            tk.abort(403, tk._("Not authorized to see this page"))

        user_list = logic.get_action("user_list")(context, data_dict)

        return tk.render(
            "admin_panel/config/user/user_list.html",
            {
                "page": self._get_pager(user_list if sort == "desc" else user_list[::-1]),
                "q": q,
                "order_by": order_by,
                "sort": sort,
                "state": state,
                "role": role,
                "bulk_options": self._get_bulk_actions(),
            },
        )

    def post(self) -> Response:
        return tk.redirect_to("ap_user.user_list")

    def _get_pager(self, users_list: list[dict[str, Any]]) -> Page:
        page_number = tk.h.get_page_number(tk.request.args)
        default_limit: int = tk.config.get("ckan.user_list_limit")
        limit = int(tk.request.args.get("limit", default_limit))

        return Page(
            collection=users_list,
            page=page_number,
            url=tk.h.pager_url,
            item_count=len(users_list),
            items_per_page=limit,
        )

    def _get_bulk_actions(self):
        return [
            {
                "value": "1",
                "text": tk._("Add the sysadmin role to the selected user(s)"),
            },
            {
                "value": "2",
                "text": tk._("Remove the Administrator role from the selected user(s)"),
            },
            {
                "value": "3",
                "text": tk._("Block the selected user(s)"),
            },
            {"value": "4", "text": tk._("Unblock the selected user(s)")},
        ]


ap_user.add_url_rule("/user_list", view_func=UserList.as_view("user_list"))
