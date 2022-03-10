from typing import TypeAlias
from typing import cast

from .encoder import bool2str
from .endpoint import Endpoint
from ..types.base import ChannelID
from ..types.base import TeamID
from ..types.base import Ts
from ..types.base import UserID
from ..types.channel import Channel
from ..types.slack.response import APIResponse
from ..types.user import User


USER_LIST: TypeAlias = list[User | UserID]


class Conversations(Endpoint):

    name = 'conversations'

    async def history(
        self,
        channel: Channel | ChannelID,
        cursor: str | None = None,
        inclusive: bool | None = None,
        latest: Ts | None = None,
        limit: int | None = None,
        oldest: Ts | None = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/conversations.history"""

        if isinstance(channel, Channel):
            channel_id = channel.id
        else:
            channel_id = channel

        params = {
            'channel': channel_id,
        }

        if inclusive is not None:
            params['inclusive'] = bool2str(inclusive)

        if latest is not None:
            params['latest'] = latest

        if limit is not None:
            params['limit'] = str(limit)

        if oldest is not None:
            params['oldest'] = oldest

        if cursor is not None:
            params['cursor'] = cursor

        return await self._call('history', params)

    async def replies(
        self,
        channel: Channel | ChannelID,
        ts: Ts,
        cursor: str | None = None,
        inclusive: bool | None = None,
        latest: Ts | None = None,
        limit: int | None = None,
        oldest: Ts | None = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/conversations.replies"""

        if isinstance(channel, Channel):
            channel_id = channel.id
        else:
            channel_id = channel

        params = {
            'channel': channel_id,
            'ts': ts,
        }

        if inclusive is not None:
            params['inclusive'] = bool2str(inclusive)

        if latest is not None:
            params['latest'] = latest

        if limit is not None:
            params['limit'] = str(limit)

        if oldest is not None:
            params['oldest'] = oldest

        if cursor is not None:
            params['cursor'] = cursor

        return await self._call('replies', params)

    async def info(
        self,
        channel: Channel | ChannelID,
        include_locale: bool | None = None,
        include_num_members: bool | None = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/conversations.info"""

        if isinstance(channel, Channel):
            channel_id = channel.id
        else:
            channel_id = channel

        params = {
            'channel': channel_id,
        }

        if include_locale is not None:
            params['include_locale'] = bool2str(include_locale)

        if include_num_members is not None:
            params['include_num_members'] = bool2str(include_num_members)

        return await self._call('info', params)

    async def list(
        self,
        cursor: str | None = None,
        exclude_archived: bool | None = None,
        limit: int | None = None,
        team_id: TeamID | None = None,
        types: str | None = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/conversations.list"""

        params = {}

        if cursor is not None:
            params['cursor'] = cursor

        if exclude_archived is not None:
            params['exclude_archived'] = bool2str(exclude_archived)

        if limit is not None:
            params['limit'] = str(limit)

        if team_id is not None:
            params['team_id'] = team_id

        if types is not None:
            params['types'] = str(types)

        return await self._call('list', params)

    async def open(
        self,
        *,
        channel: Channel | ChannelID | None = None,
        return_im: bool | None = None,
        users: USER_LIST | None = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/conversations.open"""

        if channel is None and users is None:
            raise ValueError

        if channel is not None and users is not None:
            raise ValueError

        if users is None:
            users = []

        user_ids = list(
            {
                u.id if isinstance(u, User) else u
                for u in cast(USER_LIST, users)
            }
        )

        params = {}
        if isinstance(channel, Channel):
            params['channel'] = channel.id
        elif channel is not None:
            params['channel'] = channel
        if return_im is not None:
            params['return_im'] = bool2str(return_im)
        if user_ids:
            params['users'] = ','.join(user_ids)

        return await self._call('open', params)
