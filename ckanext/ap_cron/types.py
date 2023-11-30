from __future__ import annotations

from typing import Any, TypedDict


class CronJobData(TypedDict):
    name: str
    schedule: str
    actions: str
    data: dict[str, Any]
    timeout: str


class DictizedCronJob(TypedDict):
    id: str
    name: str
    created_at: str
    updated_at: str
    last_run: str | None
    schedule: str
    actions: list[str]
    data: dict[str, Any]
    state: str
    timeout: int
