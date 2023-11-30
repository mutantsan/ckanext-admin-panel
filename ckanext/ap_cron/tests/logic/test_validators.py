from __future__ import annotations

import pytest

import ckan.model as model
import ckan.plugins.toolkit as tk

import ckanext.ap_cron.logic.validators as cron_validators
from ckanext.ap_cron.types import DictizedCronJob


class TestCronScheduleValidator:
    @pytest.mark.parametrize(
        "schedule",
        [
            "* * * * *",
            "30 * * * *",
            "0 0 * * *",
            "0 2 * * 0",
            "15 20 * * 1,3",
            "0 12 5,20 * *",
            "0 9 * * 1-5",
            "0 */3 * * *",
            "0 6 L * *",
            "0 0 15 */3 *",
            "30 16 * * 6,7",
            "*/5 * * * *",
            "0 0 1 1 *",
            "30 3 */2 * *",
            "10,25 * * * *",
            "45 7 * * 0,4",
            "10 */6 * * *",
            "0 0 29 2 *",
            "30 18 1 */3 *",
            "30 9,16 * * 5",
            "* * * JAN-DEC *",
            "* * * * MON-SUN",
            "@yearly",
            "@daily",
            "@weekly",
            "@hourly",
            "@reboot",
        ],
    )
    def test_valid_values(self, schedule):
        cron_validators.cron_schedule_validator(schedule, {})

    @pytest.mark.parametrize(
        "schedule",
        [
            "* * * *",  # Missing a field
            "* * * * * *",  # Extra field
            "60 * * * *",  # Minute field out of range
            "* 24 * * *",  # Hour field out of range
            "* * 32 * *",  # Day of month field out of range
            "* * * 13 *",  # Month field out of range
            "* * * * 8",  # Day of week field out of range
            "* /2 * * *",  # Interval without starting value
            "* */0 * * *",  # Zero interval
        ],
    )
    def test_invalid_values(self, schedule):
        with pytest.raises(
            tk.Invalid, match="The cron schedule is not properly formed"
        ):
            cron_validators.cron_schedule_validator(schedule, {})


class TestCronExistValidator:
    def test_not_exist(self):
        with pytest.raises(tk.Invalid, match="The cron job not found"):
            cron_validators.cron_job_exists("xxx", {"session": model.Session})

    @pytest.mark.usefixtures("with_plugins", "clean_db")
    def test_exist(self, cron_job: DictizedCronJob):
        cron_validators.cron_job_exists(cron_job["id"], {"session": model.Session})


@pytest.mark.usefixtures("with_plugins")
class TestCronActionExistValidator:
    def test_not_exist(self):
        with pytest.raises(tk.Invalid, match="not found"):
            cron_validators.cron_action_exists(["xxx"], {})

    def test_exist(self):
        cron_validators.cron_action_exists(["ap_cron_test_action"], {})
