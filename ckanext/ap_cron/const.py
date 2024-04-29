from enum import Enum


class CronSchedule(Enum):
    reboot = "@reboot"
    hourly = "@hourly"
    daily = "@daily"
    weekly = "@weekly"
    monthly = "@monthly"
    yearly = "@yearly"


LOG_NAME = "ap_cron"

ERRORS = "errors"
KWARGS = "kwargs"
RESULTS = "results"
