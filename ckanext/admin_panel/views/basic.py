from __future__ import annotations

from typing import Any, Union

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.lib.app_globals as app_globals
import ckan.model as model
import ckan.plugins.toolkit as tk
import ckan.logic as logic
import ckan.lib.navl.dictization_functions as dict_fns
from ckan.logic.schema import update_configuration_schema
from ckan.views.home import CACHE_PARAMETERS

from ckanext.admin_panel.utils import ap_before_request


ap_basic = Blueprint("ap_basic", __name__, url_prefix="/admin-panel")
ap_basic.before_request(ap_before_request)


class ResetConfigView(MethodView):
    def get(self) -> Union[str, Response]:
        if "cancel" in tk.request.args:
            return tk.h.redirect_to("ap_basic.config")

        return tk.render("admin/confirm_reset.html", extra_vars={})

    def post(self) -> Response:
        for item in self._get_config_items():
            model.delete_system_info(item)

        app_globals.reset()
        return tk.h.redirect_to("ap_basic.config")

    def _get_config_items(self) -> list[str]:
        return [
            "ckan.site_title",
            "ckan.theme",
            "ckan.site_description",
            "ckan.site_logo",
            "ckan.site_about",
            "ckan.site_intro_text",
            "ckan.site_custom_css",
            "ckan.homepage_style",
        ]


class ConfigView(MethodView):
    def get(self) -> str:
        return tk.render(
            "admin_panel/config/basic.html",
            extra_vars=dict(
                data={key: tk.config.get(key) for key in update_configuration_schema()},
                errors={},
                **self._get_config_options(),
            ),
        )

    def post(self) -> Union[str, Response]:
        try:
            req: dict[str, Any] = tk.request.form.copy()
            req.update(tk.request.files.to_dict())
            data_dict = logic.clean_dict(
                dict_fns.unflatten(
                    logic.tuplize_dict(
                        logic.parse_params(req, ignore_keys=CACHE_PARAMETERS)
                    )
                )
            )

            del data_dict["save"]
            tk.get_action("config_option_update")(
                {"user": tk.current_user.name}, data_dict
            )

        except tk.ValidationError as e:
            items = self._get_config_options()
            vars = dict(
                data=tk.request.form,
                errors=e.error_dict,
                error_summary=e.error_summary,
                form_items=items,
                **items,
            )
            return tk.render("admin_panel/config/basic.html", extra_vars=vars)

        return tk.h.redirect_to("ap_basic.config")

    def _get_config_options(self) -> dict[str, list[dict[str, str]]]:
        return {
            "homepages": [
                {
                    "value": "1",
                    "text": (
                        "Introductory area, search, featured"
                        " group and featured organization"
                    ),
                },
                {
                    "value": "2",
                    "text": (
                        "Search, stats, introductory area, "
                        "featured organization and featured group"
                    ),
                },
                {"value": "3", "text": "Search, introductory area and stats"},
            ]
        }


ap_basic.add_url_rule(
    "/config/reset_config", view_func=ResetConfigView.as_view("reset_config")
)
ap_basic.add_url_rule("/config/basic", view_func=ConfigView.as_view("config"))
# admin_panel_test.add_url_rule("/trash", view_func=TrashView.as_view("trash"))
