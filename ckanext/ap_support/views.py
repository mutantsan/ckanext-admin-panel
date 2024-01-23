from __future__ import annotations

from functools import partial
from typing import Any, Callable, Union

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan.lib.helpers import Page
from ckan.logic import parse_params

from ckanext.ap_main.utils import ap_before_request

from ckanext.ap_support.model import Ticket

ap_support = Blueprint(
    "ap_support",
    __name__,
    url_prefix="/admin-panel/support",
)

ap_support.before_request(ap_before_request)


class SupportListView(MethodView):
    def get(self) -> Union[str, Response]:
        return tk.render(
            "ap_support/list.html",
            extra_vars=self._prepare_data_dict(),
        )

    def _prepare_data_dict(self) -> dict[str, Any]:
        self.q = tk.request.args.get("q", "").strip()
        self.order_by = tk.request.args.get("order_by", "name")
        self.sort = tk.request.args.get("sort", "desc")

        tickets = tk.get_action("ap_support_ticket_search")(
            {}, {"q": self.q, "sort": f"{self.order_by} {self.sort}"}
        )

        return {
            "page": self._get_pager(tickets),
            "columns": self._get_table_columns(),
            "table_row_display": "ap_support/cron_table_row.html",
            "q": self.q,
            "order_by": self.order_by,
            "sort": self.sort,
            "bulk_options": self._get_bulk_action_options(),
        }

    def _get_pager(self, tickets: list[dict[str, Any]]) -> Page:
        page_number = tk.h.get_page_number(tk.request.args)
        # TODO: make configurable
        per_page = 20

        return Page(
            collection=tickets,
            page=page_number,
            url=tk.h.pager_url,
            item_count=len(tickets),
            items_per_page=per_page,
        )

    def _get_table_columns(self) -> list[dict[str, Any]]:
        return [
            tk.h.ap_table_column("id", width="5%"),
            tk.h.ap_table_column("subject", width="15%"),
            tk.h.ap_table_column("status", width="15%"),
            tk.h.ap_table_column("author", width="15%"),
            tk.h.ap_table_column("category", width="10%"),
            tk.h.ap_table_column("created_at", width="10%"),
            tk.h.ap_table_column("updated_at", width="10%"),
        ]

    def _get_bulk_action_options(self):
        return [
            {
                "value": "1",
                "text": tk._("Close selected tickets"),
            },
        ]

    def post(self) -> Response:
        bulk_action = tk.request.form.get("bulk-action")
        entity_ids = tk.request.form.getlist("entity_id")

        action_func = self._get_bulk_action(bulk_action) if bulk_action else None

        if not action_func:
            tk.h.flash_error(tk._("The bulk action is not implemented"))
            return tk.redirect_to("ap_support.manage")

        for entity_id in entity_ids:
            try:
                action_func(entity_id)
            except tk.ValidationError as e:
                tk.h.flash_error(str(e))

        return tk.redirect_to("ap_support.manage")

    def _get_bulk_action(self, value: str) -> Callable[[str], None] | None:
        return {
            "1": partial(self._change_job_state, state=Ticket.Status.closed),
            "3": self._remove_job,
        }.get(value)

    def _change_ticket_state(self, job_id: str, state: str) -> None:
        tk.get_action("ap_support_update_cron_job")(
            {"ignore_auth": True},
            {
                "id": job_id,
                "state": state,
            },
        )

    def _remove_job(self, job_id: str) -> None:
        tk.get_action("ap_support_remove_cron_job")(
            {"ignore_auth": True}, {"id": job_id}
        )


def init_modal():
    """This view inits the modal data on first open or after a submit"""

    return tk.render(
        "ap_support/ticket_modal_form.html",
    )


class AddTicketView(MethodView):
    def post(self):
        data_dict = parse_params(tk.request.form)
        data_dict["author_id"] = tk.g.userobj.id

        try:
            tk.get_action("ap_support_ticket_create")({"user": tk.g.user}, data_dict)
        except (tk.ObjectNotFound, tk.ValidationError) as e:
            return self._get_modal_body(
                title=tk._("An error occurred while creating the ticket"),
                message=str(e),
            )

        return self._get_modal_body(
            title=tk._("Your ticket has been successfully created"),
            message=tk._("View your tickets at the user account page"),
        )

    def _get_modal_body(self, title: str, message: str):
        return tk.render(
            "ap_support/ticket_modal_response.html",
            extra_vars={
                "title": title,
                "message": message,
            },
        )


ap_support.add_url_rule("/", view_func=SupportListView.as_view("list"))

# HTMX
ap_support.add_url_rule("/init_modal", view_func=init_modal)
ap_support.add_url_rule(
    "/add_ticket", view_func=AddTicketView.as_view("add_ticket"), methods=("POST",)
)
