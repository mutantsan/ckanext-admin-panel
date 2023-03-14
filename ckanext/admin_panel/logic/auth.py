# -*- coding: utf-8 -*-

from __future__ import annotations

from ckan.types import Context, DataDict, AuthResult


def admin_panel_access(context: Context, data_dict: DataDict) -> AuthResult:
    """Only sysadmins are authorized to access admin panel"""
    return {"success": False}
