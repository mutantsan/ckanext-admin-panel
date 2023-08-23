from __future__ import annotations

from typing import Any, Union
from datetime import datetime as dt

from flask import Blueprint, Response
from flask.views import MethodView
from sqlalchemy import desc, and_

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
        q = tk.request.args.get("q", "").strip()
        sort_field = tk.request.args.get("order_by", "name")
        sort_order = tk.request.args.get("sort", "desc")
        log_types = tk.request.args.getlist("type", str)
        log_levels = tk.request.args.getlist("level", int)
        start_time = tk.request.args.get("start_time")
        end_time = tk.request.args.get("end_time")

        first_item_id = tk.request.args.get("first_item_id")
        last_item_id = tk.request.args.get("last_item_id")

        per_page = 10
        current_page = tk.h.get_page_number(tk.request.args)

        query = ApLogs.session.query(ApLogs)

        if last_item_id:
            query = query.filter(ApLogs.id > last_item_id)
        elif first_item_id:
            query = query.filter(ApLogs.id < first_item_id)

        if log_levels:
            query = query.filter(ApLogs.level.in_(log_levels))

        if log_types:
            query = query.filter(ApLogs.path.in_(log_types))

        if q:
            query = query.filter(ApLogs.message_formatted.ilike(f"%{q}%"))

        if start_time and end_time and start_time > end_time:
            tk.h.flash_error(tk._("The start time must be less than the end time"))
        else:
            if start_time:
                query = query.filter(ApLogs.timestamp > dt.fromisoformat(start_time))

            if end_time:
                query = query.filter(ApLogs.timestamp < dt.fromisoformat(end_time))

        query = query.order_by(
            desc("id") if sort_order == "desc" else "id",
            # desc(sort_field) if sort_order == "desc" else sort_field
        ).limit(per_page + 1)

        has_prev = current_page > 1
        has_next = query.count() > per_page

        item_list = [log for log in query.all()]

        if has_next:
            item_list = item_list[:-1]

        return {
            "current_page": current_page,
            "item_list": item_list,
            "columns": self._get_table_columns(),
            "q": q,
            "order_by": sort_field,
            "sort": sort_order,
            "types": log_types,
            "levels": log_levels,
            "start_time": start_time,
            "end_time": end_time,
            "has_prev": has_prev,
            "has_next": has_next,
        }

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
            tk.h.ap_table_column("id", width="5%"),
            tk.h.ap_table_column("name", width="10%"),
            tk.h.ap_table_column("path", width="20%"),
            tk.h.ap_table_column("level", type_="log_level", width="5%"),
            tk.h.ap_table_column("timestamp", type_="date", width="10%"),
            tk.h.ap_table_column(
                "message", type_="text_safe", sortable=False, width="55%"
            ),
        ]

    def post(self) -> Response:
        if "clear_logs" in tk.request.form:
            ApLogs.clear_logs()
            tk.h.flash_success(tk._("Logs have been cleared."))

        return tk.redirect_to("ap_report.logs")


ap_report.add_url_rule("/reports/logs", view_func=ReportLogsView.as_view("logs"))
