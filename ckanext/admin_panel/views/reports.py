from __future__ import annotations

from typing import Any, Union

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan.lib.helpers import Page

from ckanext.admin_panel.model import ApLogs
from ckanext.admin_panel.utils import ap_before_request

ap_report = Blueprint("ap_report", __name__, url_prefix="/admin-panel")
ap_report.before_request(ap_before_request)


class ReportLogsView(MethodView):
    def get(self) -> Union[str, Response]:
        if not ApLogs.table_initialized():
            return tk.render(
                "admin_panel/config/reports/logs_disabled.html",
            )

        return tk.render(
            "admin_panel/config/reports/logs.html",
            extra_vars=self._prepare_data_dict(),
        )

    def _prepare_data_dict(self) -> dict[str, Any]:
        self.q = tk.request.args.get("q", "").strip()
        self.order_by = tk.request.args.get("order_by", "name")
        self.sort = tk.request.args.get("sort", "desc")
        self.types = tk.request.args.getlist("type", int)
        self.levels = tk.request.args.getlist("level", int)

        # TODO: replace with action log_list
        item_list = self._filter_items(ApLogs.all())
        item_list = self._search_items(item_list)
        item_list = self._sort_items(item_list)

        return {
            "page": self._get_pager(item_list),
            "columns": self._get_table_columns(),
            "q": self.q,
            "order_by": self.order_by,
            "sort": self.sort,
            "types": self.types,
            "levels": self.levels,
        }

    def _filter_items(self, item_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if self.types:
            type_options = {
                opt["value"]: opt["text"] for opt in tk.h.ap_log_list_type_options()
            }

            item_list = [
                item
                for item in item_list
                if item["name"]
                in [type_options.get(type_, type_) for type_ in self.types]
            ]

        if self.levels:
            item_list = [item for item in item_list if item["level"] in self.levels]

        return item_list

    def _search_items(self, item_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self.q:
            return item_list

        return [
            item
            for item in item_list
            if self.q.lower() in item["message_formatted"].lower()
        ]

    def _sort_items(self, item_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.order_by = tk.request.args.get("order_by", "timestamp")
        self.sort = tk.request.args.get("sort", "desc")

        return sorted(
            item_list,
            key=lambda x: x.get(self.order_by, ""),
            reverse=self.sort == "desc",
        )

    def _get_pager(self, log_list: list[dict[str, Any]]) -> Page:
        page_number = tk.h.get_page_number(tk.request.args)
        default_limit: int = tk.config.get("ckan.user_list_limit")
        limit = int(tk.request.args.get("limit", default_limit))

        return Page(
            collection=log_list,
            page=page_number,
            url=tk.h.pager_url,
            item_count=len(log_list),
            items_per_page=limit,
        )

    def _get_table_columns(self) -> list[dict[str, Any]]:
        return [
            tk.h.ap_table_column("name", width="10%"),
            tk.h.ap_table_column("path", width="20%"),
            tk.h.ap_table_column("level", column_renderer="ap_log_level", width="5%"),
            tk.h.ap_table_column("timestamp", column_renderer="ap_date", width="10%"),
            tk.h.ap_table_column("message", sortable=False, width="55%"),
        ]

    def post(self) -> Response:
        if "clear_logs" in tk.request.form:
            ApLogs.clear_logs()
            tk.h.flash_success(tk._("Logs have been cleared."))

        return tk.redirect_to("ap_report.cron")


class CronManagerView(MethodView):
    def get(self) -> Union[str, Response]:
        return tk.render(
            "admin_panel/config/reports/cron_list.html",
            extra_vars=self._prepare_data_dict(),
        )

    def _prepare_data_dict(self) -> dict[str, Any]:
        self.q = tk.request.args.get("q", "").strip()
        self.order_by = tk.request.args.get("order_by", "name")
        self.sort = tk.request.args.get("sort", "desc")

        # # TODO: it's just a mock
        cron_jobs = [
            {
                "name": "cache clear",
                "job": "ap_clear_cache",
                "time": "*/5 * * * *",
                "modified_at": "2022-08-11T12:03:30.633150",
            },
            {
                "name": "send notification to user",
                "job": "ap_send_user_notifications",
                "time": "* 12 * * *",
                "modified_at": "2022-08-11T12:03:30.633150",
            },
        ]

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
            tk.h.ap_table_column("name", width="20%"),
            tk.h.ap_table_column("job", width="40%"),
            tk.h.ap_table_column("time", width="10%", sortable=False),
            tk.h.ap_table_column(
                "modified_at",
                label="Modified at",
                column_renderer="ap_date",
                width="10%",
                sortable=False,
            ),
            tk.h.ap_table_column(
                "actions",
                column_renderer="ap_action_render",
                width="20%",
                sortable=False,
                actions=[
                    tk.h.ap_table_action(
                        "ap_content.entity_proxy",
                        label=tk._("Logs"),
                        params={
                            "entity_id": "$id",
                            "entity_type": "$type",
                            "view": "edit",
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
                        "ap_content.entity_proxy",
                        icon="fa fa-play",
                        params={
                            "entity_id": "$id",
                            "entity_type": "$type",
                            "view": "read",
                        },
                    ),
                    tk.h.ap_table_action(
                        "ap_content.entity_proxy",
                        icon="fa fa-stop",
                        params={
                            "entity_id": "$id",
                            "entity_type": "$type",
                            "view": "read",
                        },
                        attributes={"class": "btn btn-danger"},
                    ),
                    tk.h.ap_table_action(
                        "ap_content.entity_proxy",
                        icon="fa fa-trash-alt",
                        params={
                            "entity_id": "$id",
                            "entity_type": "$type",
                            "view": "read",
                        },
                        attributes={"class": "btn btn-danger"},
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
            }
        ]

    def post(self) -> Response:
        return tk.redirect_to("ap_report.cron")


ap_report.add_url_rule("/reports/logs", view_func=ReportLogsView.as_view("logs"))
ap_report.add_url_rule("/reports/cron", view_func=CronManagerView.as_view("cron"))
