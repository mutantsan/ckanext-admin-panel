from __future__ import annotations

from typing import Union, Any

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk

from ckanext.admin_panel.utils import ap_before_request
from ckanext.admin_panel.model import ApLogs
from ckan.lib.helpers import Page

ap_report = Blueprint("ap_report", __name__, url_prefix="/admin-panel")
ap_report.before_request(ap_before_request)


class ReportLogsView(MethodView):
    def get(self) -> Union[str, Response]:
        log_items = ApLogs.all()

        return tk.render(
            "admin_panel/config/reports/logs.html",
            extra_vars={"page": self._get_pager(log_items)},
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

    def post(self) -> Response:
        return tk.redirect_to("ap_user.list")


ap_report.add_url_rule("/reports/logs", view_func=ReportLogsView.as_view("logs"))
