import ckan.plugins as p
import ckan.plugins.toolkit as toolkit

from ckanext.admin_panel.views import get_blueprints
from ckanext.admin_panel.logic.auth import get_auth_functions

class AdminPanelPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IBlueprint)
    p.implements(p.IAuthFunctions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "admin_panel")

    # IBlueprint

    def get_blueprint(self):
        return get_blueprints()

    # IAuthFunctions

    def get_auth_functions(self):
        return get_auth_functions()
