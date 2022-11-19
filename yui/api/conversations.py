from typing import List

from ..types.base import ChannelID
from ..types.base import Ts
from ..types.base import UserID
from ..types.slack.response import APIResponse
from .encoder import bool2str
from .endpoint import Endpoint


class Conversations(Endpoint):

    name = "conversations"

    async def history(
        self,
        channel: ChannelID,
        cursor: str | None = None,
        inclusive: bool | None = None,
        latest: Ts | None = None,
        limit: int | None = None,
        oldest: Ts | None = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/conversations.history"""

        params = {
            "channel": str(channel),
        }

        if inclusive is not None:
            params["inclusive"] = bool2str(inclusive)

        if latest is not None:
            params["latest"] = latest

        if limit is not None:
            params["limit"] = str(limit)

        if oldest is not None:
            params["oldest"] = oldest

        if cursor is not None:
            params["cursor"] = cursor

        return await self._call("history", params)

    async def replies(
        self,
        channel: ChannelID,
        ts: Ts,
        cursor: str | None = None,
        inclusive: bool | None = None,
        latest: Ts | None = None,
        limit: int | None = None,
        oldest: Ts | None = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/conversations.replies"""

        params = {
            "channel": str(channel),
            "ts": str(ts),
        }

        if inclusive is not None:
            params["inclusive"] = bool2str(inclusive)

        if latest is not None:
            params["latest"] = latest

        if limit is not None:
            params["limit"] = str(limit)

        if oldest is not None:
            params["oldest"] = oldest

        if cursor is not None:
            params["cursor"] = cursor

        return await self._call("replies", params)

    async def info(
        self,
        channel: ChannelID,
        include_locale: bool | None = None,
        include_num_members: bool | None = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/conversations.info"""

        params = {
            "channel": str(channel),
        }

        if include_locale is not None:
            params["include_locale"] = bool2str(include_locale)

        if include_num_members is not None:
            params["include_num_members"] = bool2str(include_num_members)

        return await self._call("info", params)

    async def list(
        self,
        cursor: str | None = None,
        exclude_archived: bool | None = None,
        limit: int | None = None,
        team_id: str | None = None,
        types: str | None = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/conversations.list"""

        params = {}

        if cursor is not None:
            params["cursor"] = cursor

        if exclude_archived is not None:
            params["exclude_archived"] = bool2str(exclude_archived)

        if limit is not None:
            params["limit"] = str(limit)

        if team_id is not None:
            params["team_id"] = team_id

        if types is not None:
            params["types"] = str(types)

        return await self._call("list", params)

    async def open(
        self,
        *,
        channel: ChannelID | None = None,
        return_im: bool | None = None,
        users: List[UserID] | None = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/conversations.open"""

        if channel is None and users is None:
            raise ValueError

        if channel is not None and users is not None:
            raise ValueError

        if users is None:
            users = []

        params = {}
        if channel is not None:
            params["channel"] = str(channel)

        if return_im is not None:
            params["return_im"] = bool2str(return_im)
        if users:
            params["users"] = ",".join(map(str, users))

        return await self._call("open", params)
