from __future__ import annotations

from typing import Optional, TypedDict


class SectionConfig(TypedDict):
    name: str
    configs: list["ConfigurationItem"]


class ConfigurationItem(TypedDict, total=False):
    name: str
    blueprint: str
    info: Optional[str]
