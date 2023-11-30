from __future__ import annotations

import pytest

import ckan.model as model
import ckan.plugins.toolkit as tk
from ckan.tests.helpers import call_auth


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestCronAuth:
    """For now, every action is available only for sysadmin. Therefore, there
    is no need for thorough testing."""

    def test_anon(self):
        with pytest.raises(tk.NotAuthorized):
            call_auth("ap_cron_add_job", context={"user": None, "model": model})

    def test_regular_user(self, user):
        with pytest.raises(tk.NotAuthorized):
            call_auth("ap_cron_add_job", context={"user": user["name"], "model": model})

    def test_sysadmin(self, sysadmin):
        call_auth("ap_cron_add_job", context={"user": sysadmin["name"], "model": model})
