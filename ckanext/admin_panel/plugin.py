import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckanext.admin_panel.views import get_blueprints
from ckanext.admin_panel.logic.auth import get_auth_functions


@tk.blanket.helpers
class AdminPanelPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IBlueprint)
    p.implements(p.IAuthFunctions)
    p.implements(p.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "admin_panel")

    # IBlueprint

    def get_blueprint(self):
        return get_blueprints()

    # IAuthFunctions

    def get_auth_functions(self):
        return get_auth_functions()
