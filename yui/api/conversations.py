from typing import Optional
from typing import Union
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


USER_LIST = list[Union[User, UserID]]


class Conversations(Endpoint):

    name = 'conversations'

    async def history(
        self,
        channel: Union[Channel, ChannelID],
        cursor: Optional[str] = None,
        inclusive: Optional[bool] = None,
        latest: Optional[Ts] = None,
        limit: Optional[int] = None,
        oldest: Optional[Ts] = None,
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
        channel: Union[Channel, ChannelID],
        ts: Ts,
        cursor: Optional[str] = None,
        inclusive: Optional[bool] = None,
        latest: Optional[Ts] = None,
        limit: Optional[int] = None,
        oldest: Optional[Ts] = None,
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
        channel: Union[Channel, ChannelID],
        include_locale: Optional[bool] = None,
        include_num_members: Optional[bool] = None,
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
        cursor: Optional[str] = None,
        exclude_archived: Optional[bool] = None,
        limit: Optional[int] = None,
        team_id: Optional[TeamID] = None,
        types: Optional[str] = None,
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
        channel: Optional[Union[Channel, ChannelID]] = None,
        return_im: Optional[bool] = None,
        users: Optional[USER_LIST] = None,
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
