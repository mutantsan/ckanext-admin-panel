from __future__ import annotations

from typing import Any, Union

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.lib.app_globals as app_globals
import ckan.model as model
import ckan.plugins.toolkit as tk
import ckan.logic as logic
import ckan.lib.navl.dictization_functions as dict_fns
from ckan.types import Query
from ckan.logic.schema import update_configuration_schema
from ckan.views.home import CACHE_PARAMETERS

from ckanext.admin_panel.utils import ap_before_request


ap_basic = Blueprint("ap_basic", __name__, url_prefix="/admin-panel")
ap_basic.before_request(ap_before_request)


class ResetView(MethodView):
    def get(self) -> Union[str, Response]:
        if "cancel" in tk.request.args:
            return tk.redirect_to("ap_basic.config")
        return tk.render("admin_panel/config/confirm_reset.html")

    def post(self) -> Response:
        for item in self._get_config_items():
            model.delete_system_info(item)

        app_globals.reset()
        return tk.redirect_to("ap_basic.config")

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

        tk.h.flash_success(tk._("Settings have been saved"))

        return tk.redirect_to("ap_basic.config")

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


class EditableConfigView(MethodView):
    """Adapter for ckanext-editable-config.

    Once this extension get stable API, remove this logic and implement proper
    hooks inside ckanext-editable-config.

    """

    def _render(
        self,
        data: dict[str, Any] | None = None,
        error: tk.ValidationError | None = None,
    ):
        """Shared method for normal GET and failed POST request."""
        options = tk.get_action("editable_config_list")({}, {})

        extra_vars: dict[str, Any] = {
            "data": data or {},
            "options": options,
            "errors": error.error_dict if error else None,
            "error_summary": error.error_summary if error else None,
        }

        return tk.render("admin_panel/config/editable_config.html", extra_vars)

    def get(self) -> str:
        return self._render()

    def post(self) -> Union[str, Response]:
        data = logic.parse_params(tk.request.form)

        change: dict[str, Any] = {}
        reset: list[str] = []

        for key in data:
            if key.startswith("reset:"):
                # remove any customization from option if Reset checkbox is
                # checked.
                clean_key = key[6:]
                change.pop(clean_key, None)
                reset.append(clean_key)

            else:
                if key in reset:
                    # don't try to modify options that will be removed. It
                    # won't change the result. This condition exists merely for
                    # optimization
                    continue
                change[key] = data[key]

        try:
            tk.get_action("editable_config_update")(
                {},
                {"change": change, "reset": reset},
            )
        except tk.ValidationError as e:
            return self._render(data, e)

        tk.h.flash_success(tk._("Settings have been saved"))
        return tk.redirect_to("ap_basic.editable_config")


class TrashView(MethodView):
    def __init__(self):
        self.deleted_packages = self._get_deleted_datasets()
        self.deleted_orgs = model.Session.query(model.Group).filter_by(
            state=model.State.DELETED, is_organization=True
        )
        self.deleted_groups = model.Session.query(model.Group).filter_by(
            state=model.State.DELETED, is_organization=False
        )

        self.deleted_entities = {
            "package": self.deleted_packages,
            "organization": self.deleted_orgs,
            "group": self.deleted_groups,
        }
        self.messages = {
            "confirm": {
                "all": tk._("Are you sure you want to purge everything?"),
                "package": tk._("Are you sure you want to purge datasets?"),
                "organization": tk._("Are you sure you want to purge organizations?"),
                "group": tk._("Are you sure you want to purge groups?"),
            },
            "success": {
                "package": tk._("{number} datasets have been purged"),
                "organization": tk._("{number} organizations have been purged"),
                "group": tk._("{number} groups have been purged"),
            },
            "empty": {
                "package": tk._("There are no datasets to purge"),
                "organization": tk._("There are no organizations to purge"),
                "group": tk._("There are no groups to purge"),
            },
        }

    def _get_deleted_datasets(self) -> Union["Query[model.Package]", list[Any]]:
        if tk.config.get("ckan.search.remove_deleted_packages"):
            return self._get_deleted_datasets_from_db()
        else:
            return self._get_deleted_datasets_from_search_index()

    def _get_deleted_datasets_from_db(self) -> "Query[model.Package]":
        return model.Session.query(model.Package).filter_by(state=model.State.DELETED)

    def _get_deleted_datasets_from_search_index(self) -> list[Any]:
        results = tk.get_action("package_search")(
            {"ignore_auth": True},
            {
                "fq": "+state:deleted",
                "include_private": True,
            },
        )

        return results["results"]

    def get(self) -> str:
        ent_type: str | None = tk.request.args.get("name")

        if ent_type:
            return tk.render(
                "admin_panel/config/snippets/confirm_delete.html",
                extra_vars={"ent_type": ent_type, "messages": self.messages},
            )

        return tk.render(
            "admin_panel/config/trash.html",
            extra_vars={"data": self.deleted_entities, "messages": self.messages},
        )

    def post(self) -> Response:
        if "cancel" in tk.request.form:
            return tk.h.redirect_to("ap_basic.trash")

        req_action: str = tk.request.form.get("action", "")

        if req_action == "all":
            self.purge_all()
        elif req_action in ("package", "organization", "group"):
            self.purge_entity(req_action)
        else:
            tk.h.flash_error(tk._("Action not implemented."))

        return tk.h.redirect_to("ap_basic.trash")

    def purge_all(self):
        actions = ("dataset_purge", "group_purge", "organization_purge")
        entities = (self.deleted_packages, self.deleted_groups, self.deleted_orgs)

        for action, deleted_entities in zip(actions, entities):
            for entity in deleted_entities:
                ent_id: str = entity.id if hasattr(entity, "id") else entity["id"]
                tk.get_action(action)({"user": tk.current_user.name}, {"id": ent_id})
            model.Session.remove()
        tk.h.flash_success(tk._("Massive purge complete"))

    def purge_entity(self, ent_type: str):
        entities = self.deleted_entities[ent_type]
        number = len(entities) if type(entities) == list else entities.count()

        for ent in entities:
            entity_id: str = ent.id if hasattr(ent, "id") else ent["id"]
            tk.get_action(self._get_purge_action(ent_type))(
                {"user": tk.current_user.name}, {"id": entity_id}
            )

        model.Session.remove()
        tk.h.flash_success(self.messages["success"][ent_type].format(number=number))

    @staticmethod
    def _get_purge_action(ent_type: str) -> str:
        actions = {
            "package": "dataset_purge",
            "organization": "organization_purge",
            "group": "group_purge",
        }

        return actions[ent_type]


ap_basic.add_url_rule("/config/basic", view_func=ConfigView.as_view("config"))
ap_basic.add_url_rule(
    "/config/editable-config", view_func=EditableConfigView.as_view("editable_config")
)
ap_basic.add_url_rule("/config/basic/reset", view_func=ResetView.as_view("reset"))
ap_basic.add_url_rule("/config/basic/trash", view_func=TrashView.as_view("trash"))
