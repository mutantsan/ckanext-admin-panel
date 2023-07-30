import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckanext.admin_panel.views import get_blueprints


@tk.blanket.helpers
@tk.blanket.auth_functions
class AdminPanelPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IBlueprint)

    # IConfigurer

    def update_config(self, config_: tk.CKANConfig):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "admin_panel")

    # IBlueprint

    def get_blueprint(self):
        return get_blueprints()
