from __future__ import annotations

from typing import Any, Optional, TypedDict


class SectionConfig(TypedDict):
    name: str
    configs: list["ConfigurationItem"]


class ConfigurationItem(TypedDict, total=False):
    name: str
    blueprint: str
    info: Optional[str]


class ToolbarButton(TypedDict, total=False):
    label: str
    url: Optional[str]
    icon: Optional[str]
    attributes: Optional[dict[str, Any]]
    subitems: list["ToolbarButton"]
