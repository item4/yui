from typing import Optional, Union

from .encoder import bool2str
from .endpoint import Endpoint
from ..types.base import PublicChannelID, Ts
from ..types.channel import PublicChannel
from ..types.slack.response import APIResponse


class Channels(Endpoint):

    name = 'channels'

    async def history(
        self,
        channel: Union[PublicChannel, PublicChannelID],
        count: Optional[int] = None,
        inclusive: Optional[bool] = None,
        latest: Optional[Ts] = None,
        oldest: Optional[Ts] = None,
        unreads: Optional[bool] = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/channels.history"""

        if isinstance(channel, PublicChannel):
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
        channel: Union[PublicChannel, PublicChannelID],
        include_locale: bool = False,
    ) -> APIResponse:
        """https://api.slack.com/methods/channels.info"""

        if isinstance(channel, PublicChannel):
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
    ) -> APIResponse:
        """https://api.slack.com/methods/channels.list"""

        params = {
            'exclude_archived': bool2str(exclude_archived),
            'exclude_members': bool2str(exclude_members),
            'limit': str(limit),
        }
        if cursor:
            params['cursor'] = cursor

        return await self._call('list', params)
