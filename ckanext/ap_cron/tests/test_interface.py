from __future__ import annotations

import pytest

import ckan.plugins.toolkit as tk
from ckan.tests import factories


@pytest.mark.usefixtures("non_clean_db", "with_plugins")
class TestApCronInterace(object):
    def test_action_without_exclude(self, app, sysadmin):
        url = tk.h.url_for("ap_cron.action_autocomplete")

        user_token = factories.APIToken(user=sysadmin["name"])

        result = app.get(
            url=url,
            headers={"Authorization": user_token["token"]},  # type: ignore
            query_string={"incomplete": "test"},
        ).json

        # I've excluded "ap_cron_test_action_2" in ApCronTestPlugin
        assert len(result["ResultSet"]["Result"]) == 2
