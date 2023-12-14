from __future__ import annotations

from ckan.plugins.interfaces import Interface
from ckan import types


class IAPCron(Interface):
    def exclude_action(
        self, action_list: dict[str, types.Action]
    ) -> dict[str, types.Action]:
        """By default, all the CKAN actions could be used by cron job. This method
        provides a possibiltiy to make an actions non-usable."""
        return action_list
