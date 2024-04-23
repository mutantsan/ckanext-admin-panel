import ckan.plugins.toolkit as tk


def is_mock_api_calls() -> bool:
    return tk.asbool(tk.config.get("ckanext.ap_doi.mock_api_calls"))


def get_doi_prefix() -> str:
    return tk.config.get("ckanext.doi.prefix")
