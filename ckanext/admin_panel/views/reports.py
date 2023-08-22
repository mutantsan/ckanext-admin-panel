from __future__ import annotations

from typing import Union, Any

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk

from ckanext.admin_panel.utils import ap_before_request
from ckanext.admin_panel.model import ApLogs
from ckan.lib.helpers import Page

from ckanext.admin_panel.helpers import ap_table_column as ap_column

ap_report = Blueprint("ap_report", __name__, url_prefix="/admin-panel")
ap_report.before_request(ap_before_request)


class ReportLogsView(MethodView):
    def get(self) -> Union[str, Response]:
        self.q = tk.request.args.get("q", "").strip()
        self.order_by = tk.request.args.get("order_by", "name")
        self.sort = tk.request.args.get("sort", "desc")
        self.type = tk.request.args.getlist("type")
        self.level = tk.request.args.getlist("level")

        return tk.render(
            "admin_panel/config/reports/logs.html",
            extra_vars=self._prepare_data_dict(),
        )

    def _prepare_data_dict(self) -> dict[str, Any]:
        return {
            "page": self._get_pager(ApLogs.all()),
            "columns": self._get_table_columns(),
            "q": self.q,
            "order_by": self.order_by,
            "sort": self.sort,
            "type": self.type,
            "level": self.level,
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
            ap_column("name", width="10%"),
            ap_column("path", width="20%"),
            ap_column("level",width="5%"),
            ap_column("timestamp", type_="date", width="10%"),
            ap_column("message", sortable=False, width="55%"),
        ]

    def post(self) -> Response:
        return tk.redirect_to("ap_user.list")


ap_report.add_url_rule("/reports/logs", view_func=ReportLogsView.as_view("logs"))
