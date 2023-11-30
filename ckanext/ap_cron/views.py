from __future__ import annotations

import json

from typing import Any, Union, cast
from ckan import types

from flask import Blueprint, Response, jsonify, make_response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan.lib.helpers import Page

from ckanext.ap_main.utils import ap_before_request
from ckanext.ap_cron import types as cron_types
from ckanext.ap_cron.const import LOG_NAME

ap_cron = Blueprint(
    "ap_cron",
    __name__,
    url_prefix="/admin-panel/cron",
)
ap_cron.before_request(ap_before_request)


class CronManagerView(MethodView):
    def get(self) -> Union[str, Response]:
        return tk.render(
            "ap_cron/cron_list.html",
            extra_vars=self._prepare_data_dict(),
        )

    def _prepare_data_dict(self) -> dict[str, Any]:
        self.q = tk.request.args.get("q", "").strip()
        self.order_by = tk.request.args.get("order_by", "name")
        self.sort = tk.request.args.get("sort", "desc")

        cron_jobs = tk.get_action("ap_cron_get_cron_job_list")({}, {})

        cron_jobs = self._search_items(cron_jobs)
        cron_jobs = self._sort_items(cron_jobs)

        return {
            "page": self._get_pager(cron_jobs),
            "columns": self._get_table_columns(),
            "q": self.q,
            "order_by": self.order_by,
            "sort": self.sort,
            "bulk_options": self._get_bulk_action_options(),
        }

    def _search_items(self, item_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self.q:
            return item_list

        return [item for item in item_list if self.q.lower() in item["name"].lower()]

    def _sort_items(self, item_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.order_by = tk.request.args.get("order_by", "timestamp")
        self.sort = tk.request.args.get("sort", "desc")

        return sorted(
            item_list,
            key=lambda x: x.get(self.order_by, ""),
            reverse=self.sort == "desc",
        )

    def _get_pager(self, cron_jobs: list[dict[str, Any]]) -> Page:
        page_number = tk.h.get_page_number(tk.request.args)
        default_limit: int = tk.config.get("ckan.user_list_limit")
        limit = int(tk.request.args.get("limit", default_limit))

        return Page(
            collection=cron_jobs,
            page=page_number,
            url=tk.h.pager_url,
            item_count=len(cron_jobs),
            items_per_page=limit,
        )

    def _get_table_columns(self) -> list[dict[str, Any]]:
        return [
            tk.h.ap_table_column("name", width="15%"),
            tk.h.ap_table_column("actions", column_renderer="ap_list", width="15%"),
            tk.h.ap_table_column(
                "data",
                column_renderer="ap_cron_json_display",
                width="30%",
                sortable=False,
            ),
            tk.h.ap_table_column(
                "schedule",
                column_renderer="ap_cron_schedule",
                width="10%",
                sortable=False,
            ),
            tk.h.ap_table_column(
                "last_run",
                label="Last run",
                column_renderer="ap_cron_last_run",
                width="10%",
                sortable=False,
            ),
            tk.h.ap_table_column(
                "state",
                label="State",
                width="5%",
                sortable=False,
            ),
            tk.h.ap_table_column(
                "actions",
                column_renderer="ap_action_render",
                width="15%",
                sortable=False,
                actions=[
                    tk.h.ap_table_action(
                        "ap_report.logs",
                        label=tk._("Logs"),
                        params={
                            "type": LOG_NAME,
                            "q": "$id",
                        },
                        attributes={"class": "btn btn-black"},
                    ),
                    tk.h.ap_table_action(
                        "ap_content.entity_proxy",
                        label=tk._("Edit"),
                        params={
                            "entity_id": "$id",
                            "entity_type": "$type",
                            "view": "edit",
                        },
                    ),
                    tk.h.ap_table_action(
                        "ap_cron.run",
                        icon="fa fa-play",
                        params={
                            "job_id": "$id",
                        },
                    ),
                    tk.h.ap_table_action(
                        "ap_cron.delete",
                        icon="fa fa-trash-alt",
                        params={
                            "job_id": "$id",
                        },
                        attributes={
                            "class": "btn btn-danger",
                            "hx-swap": "none",
                            "hx-trigger": "click",
                            "hx-post": lambda item: tk.h.url_for(
                                "ap_cron.delete", job_id=item["id"]
                            ),
                        },
                    ),
                ],
            ),
        ]

    def _get_bulk_action_options(self):
        return [
            {
                "value": "1",
                "text": tk._("Disable selected job"),
            },
            {
                "value": "2",
                "text": tk._("Enable selected job"),
            },
            {
                "value": "3",
                "text": tk._("Delete selected job"),
            },
        ]


class CronAddView(MethodView):
    def post(self) -> Response:
        data_dict, errors = self._prepare_payload()

        if errors:
            tk.h.flash_error(errors)
            return tk.redirect_to("ap_cron.manage")

        try:
            tk.get_action("ap_cron_add_cron_job")(
                {
                    "user": tk.current_user.name,
                    "auth_user_obj": tk.current_user,
                },
                cast(types.DataDict, data_dict),
            )
        except tk.ValidationError as e:
            tk.h.flash_error(e)
            return tk.redirect_to("ap_cron.manage")

        tk.h.flash_success(tk._("The cron job has been created!"))

        return tk.redirect_to("ap_cron.manage")

    def _prepare_payload(self) -> tuple[cron_types.CronJobData | None, dict[str, Any]]:
        errors = {}

        try:
            data = tk.request.form.get("job_data", "{}")
            data = json.loads(data)
        except ValueError:
            tk.h.flash_error(errors)
            errors["data"] = tk._("Cron job data must be a valid JSON")
            return None, errors

        result = cron_types.CronJobData(
            name=tk.request.form.get("name", ""),
            schedule=tk.request.form.get("schedule", ""),
            actions=tk.request.form.get("actions", ""),
            data={"kwargs": data},
            timeout=tk.request.form.get("timeout", ""),
        )

        return result, errors


class CronDeleteJobView(MethodView):
    def post(self, job_id: str) -> str:
        try:
            tk.get_action("ap_cron_remove_cron_job")(
                {},
                cast(types.DataDict, {"id": job_id}),
            )
        except tk.ValidationError as e:
            pass

        return ""


class CronRunJobView(MethodView):
    """Initially I wanted to make it with HTMX. Having a get endpoint for such
    an action is a bit wrong."""

    def get(self, job_id: str) -> Response:
        try:
            result = tk.get_action("ap_cron_run_cron_job")(
                {},
                cast(types.DataDict, {"id": job_id}),
            )
        except tk.ValidationError as e:
            tk.h.flash_error(e.error_dict["message"])
            return tk.redirect_to("ap_cron.manage")

        tk.h.flash_success(
            f"The cron job \"{result['job']['name']}\" has been started!"
        )
        return tk.redirect_to("ap_cron.manage")


def action_autocomplete() -> Response:
    q = tk.request.args.get("incomplete", "")
    limit = tk.request.args.get("limit", 10)

    actions: list[dict[str, str]] = []

    if q:
        from ckan.logic import _actions

        actions = [{"Name": action} for action in _actions if q in action][:limit]

    return make_response(jsonify({"ResultSet": {"Result": actions}}))


ap_cron.add_url_rule("/", view_func=CronManagerView.as_view("manage"))
ap_cron.add_url_rule("/add", view_func=CronAddView.as_view("add"))
ap_cron.add_url_rule("/delete/<job_id>", view_func=CronDeleteJobView.as_view("delete"))
ap_cron.add_url_rule("/run/<job_id>", view_func=CronRunJobView.as_view("run"))


# API
ap_cron.add_url_rule("/util/action/autocomplete", view_func=action_autocomplete)
