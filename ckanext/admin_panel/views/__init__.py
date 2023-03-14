from ckanext.admin_panel.views.basic import ap_basic
from ckanext.admin_panel.views.config import ap_config_list


def get_blueprints():
    return [ap_basic, ap_config_list]
