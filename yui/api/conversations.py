from typing import List, Optional, Union

from .encoder import bool2str
from .endpoint import Endpoint
from ..types.base import ChannelID, Ts, UserID
from ..types.channel import Channel
from ..types.slack.response import APIResponse
from ..types.user import User


class Conversations(Endpoint):

    name = 'conversations'

    async def history(
        self,
        channel: Union[Channel, ChannelID],
        count: Optional[int] = None,
        inclusive: Optional[bool] = None,
        latest: Optional[Ts] = None,
        oldest: Optional[Ts] = None,
        unreads: Optional[bool] = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/conversations.history"""

        if isinstance(channel, Channel):
            channel_id = channel.id
        else:
            channel_id = channel

        params = {
            'channel': channel_id,
        }

        if count is not None:
            params['count'] = str(count)

        if inclusive is not None:
            params['inclusive'] = bool2str(inclusive)

        if latest is not None:
            params['latest'] = latest

        if oldest is not None:
            params['oldest'] = oldest

        if unreads is not None:
            params['unreads'] = bool2str(unreads)

        return await self._call('history', params)

    async def info(
        self,
        channel: Union[Channel, ChannelID],
        include_locale: bool = False,
    ) -> APIResponse:
        """https://api.slack.com/methods/conversations.info"""

        if isinstance(channel, Channel):
            channel_id = channel.id
        else:
            channel_id = channel

        return await self._call(
            'info',
            {
                'channel': channel_id,
                'include_locale': bool2str(include_locale),
            }
        )

    async def list(
        self,
        cursor: Optional[str] = None,
        exclude_archived: bool = True,
        exclude_members: bool = True,
        limit: int = 0,
        types: str = 'public_channel',
    ) -> APIResponse:
        """https://api.slack.com/methods/conversations.list"""

        params = {
            'exclude_archived': bool2str(exclude_archived),
            'exclude_members': bool2str(exclude_members),
            'limit': str(limit),
            'types': types,
        }
        if cursor:
            params['cursor'] = cursor

        return await self._call('list', params)

    async def open(
        self,
        *,
        channel: Optional[Union[Channel, ChannelID]] = None,
        return_im: Optional[bool] = None,
        users: Optional[List[Union[User, UserID]]] = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/conversations.open"""

        if channel is None and users is None:
            raise ValueError

        if channel is not None and users is not None:
            raise ValueError

        if users is None:
            users = []
        user_ids = [
            u if isinstance(u, str) else u.id for u in users
        ]
        channel_id = None
        if isinstance(channel, Channel):
            channel_id = channel.id
        else:
            channel_id = channel

        params = {}
        if channel_id is not None:
            params['channel'] = channel_id
        if return_im is not None:
            params['return_im'] = bool2str(return_im)
        if user_ids:
            params['users'] = ','.join(user_ids)

        return await self._call('open', params)
