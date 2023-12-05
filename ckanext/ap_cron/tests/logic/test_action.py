import pytest
import unittest.mock as mock

import ckan.plugins.toolkit as tk
from ckan.tests.helpers import call_action

import ckanext.ap_cron.config as cron_conf
from ckanext.ap_cron.model import CronJob
from ckanext.ap_cron.types import DictizedCronJob


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestCronJobCreate:
    def test_basic_create(self, cron_job_factory):
        job: DictizedCronJob = cron_job_factory()

        assert job["id"]
        assert job["name"]
        assert job["created_at"]
        assert job["updated_at"]
        assert job["last_run"] is None
        assert job["schedule"] == "* * * * *"
        assert job["timeout"] == cron_conf.get_job_timeout()
        assert job["state"] == CronJob.State.new

        assert isinstance(job["data"], dict)
        assert isinstance(job["actions"], list)


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestCronJobUpdate:
    def test_basic_update(self, cron_job: DictizedCronJob):
        assert cron_job["last_run"] is None

        payload = dict(
            id=cron_job["id"],
            name="new name",
            schedule="@yearly",
            actions=["ap_cron_test_action", "ap_cron_test_action_2"],
            timeout=999,
            state=CronJob.State.running,
            data={"kwargs": {"new_data": 1}},
        )

        result: DictizedCronJob = call_action("ap_cron_update_cron_job", **payload)

        for key, value in payload.items():
            assert result[key] == value

        assert result["updated_at"] != cron_job["updated_at"]


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestCronJobGet:
    def test_basic_get(self, cron_job: DictizedCronJob):
        result: DictizedCronJob = call_action("ap_cron_get_cron_job", id=cron_job["id"])

        assert result["id"] == cron_job["id"]

    def test_basic_get_missing(self):
        with pytest.raises(tk.ValidationError, match="The cron job not found"):
            call_action("ap_cron_get_cron_job", id="xxx")


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestCronJobRemove:
    def test_basic_remove(self, cron_job: DictizedCronJob):
        result: DictizedCronJob = call_action(
            "ap_cron_remove_cron_job", id=cron_job["id"]
        )

        assert result is True

    def test_basic_remove_missing(self):
        with pytest.raises(tk.ValidationError, match="The cron job not found"):
            call_action("ap_cron_remove_cron_job", id="xxx")


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestCronJobList:
    def test_basic_list_empty(self):
        result = call_action("ap_cron_get_cron_job_list")

        assert len(result) == 0

    def test_basic_list(self, cron_job: DictizedCronJob):
        result = call_action("ap_cron_get_cron_job_list")

        assert len(result) == 1

    def test_basic_list_filter_state(self, cron_job_factory):
        """You can pass a list of states to sort by them"""
        cron_job_factory(states=[CronJob.State.running])

        result = call_action("ap_cron_get_cron_job_list")

        assert len(result) == 1


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestCronJobRun:
    @mock.patch("ckanext.ap_cron.logic.action.enqueue_cron_job")
    def test_basic_run(self, enqueue_mock, cron_job: DictizedCronJob):
        enqueue_mock.return_value = True
        assert enqueue_mock.call_count == 0

        call_action("ap_cron_run_cron_job", id=cron_job["id"])

        assert enqueue_mock.call_count == 1
