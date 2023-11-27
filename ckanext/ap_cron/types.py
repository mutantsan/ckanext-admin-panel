from __future__ import annotations

from typing import Any, TypedDict


class CronJobData(TypedDict):
    name: str
    schedule: str
    data: dict[str, Any]
