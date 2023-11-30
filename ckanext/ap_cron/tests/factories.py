from __future__ import annotations

from typing import Any

import factory

import ckan.types as types
import ckan.plugins as plugins
from ckan.tests import factories

from ckanext.ap_cron.model import CronJob
from ckanext.ap_cron import config as cron_conf


class ApCronPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)

    @staticmethod
    def ap_cron_test_action(context: types.Context, data_dict: types.DataDict):
        return data_dict

    @staticmethod
    def ap_cron_test_action_2(context: types.Context, data_dict: types.DataDict):
        return data_dict

    def get_actions(self) -> dict[str, types.Action]:
        return {
            "ap_cron_test_action": self.ap_cron_test_action,
            "ap_cron_test_action_2": self.ap_cron_test_action_2,
        }


class CronJobFactory(factories.CKANFactory):
    class Meta:
        model = CronJob
        action = "ap_cron_add_cron_job"

    id = factory.Faker("uuid4")
    name = factory.Faker("sentence")
    created_at = factory.Faker("date_this_month")
    updated_at = factory.Faker("date_this_month")
    last_run = None
    schedule = "* * * * *"
    actions = "ap_cron_test_action"
    data = {"foo": "baar"}
    timeout = factory.LazyAttribute(lambda _: cron_conf.get_job_timeout())
