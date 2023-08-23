from __future__ import annotations

from redis import ConnectionPool, Redis

import ckan.plugins.toolkit as tk

from ckanext.admin_panel.model import ApLogs

_ap_connection_pool = None


def ap_before_request() -> None:
    try:
        tk.check_access(
            "admin_panel_access",
            {"user": tk.current_user.name},
        )
    except tk.NotAuthorized:
        tk.abort(403, tk._("Need to be system administrator to administer"))


def add_log_type(log_type: str) -> None:
    """Save a log type to redis, to render a type filter later"""
    conn = connect_to_redis()
    conn.sadd("ckanext-ap:logs:log_types", log_type)
    conn.close()


def get_log_types() -> list[str]:
    """retrieve a log types from redis, to render a type filter"""
    conn = connect_to_redis()
    result = conn.smembers("ckanext-ap:logs:log_types")
    conn.close()

    return [type_.decode("utf-8") for type_ in result]


def connect_to_redis() -> Redis:
    global _ap_connection_pool

    if _ap_connection_pool is None:
        _ap_connection_pool = ConnectionPool.from_url(ApLogs.redis_uri)

    return Redis(connection_pool=_ap_connection_pool)
