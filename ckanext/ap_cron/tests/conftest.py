import pytest

from faker import Faker
from pytest_factoryboy import register

from ckan.plugins import load_all

import ckanext.ap_cron.tests.factories as local_factories

fake = Faker()

register(local_factories.CronJobFactory, "cron_job")


@pytest.fixture()
def clean_db(reset_db, migrate_db_for):
    reset_db()
    _migrate_plugins(migrate_db_for)


@pytest.fixture(scope="session")
def reset_db_once(reset_db, migrate_db_for):
    """Dependency of `non_clean_db`"""
    load_all()
    reset_db()
    _migrate_plugins(migrate_db_for)


def _migrate_plugins(migrate_db_for):
    migrate_db_for("admin_panel")
    migrate_db_for("admin_panel_cron")
