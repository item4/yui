from typing import Optional, Union

from .endpoint import Endpoint
from ..type import PublicChannel, PublicChannelID
from ..util import bool2str

__all__ = 'Channels',


class Channels(Endpoint):

    name = 'channels'

    async def info(
        self,
        channel: Union[PublicChannel, PublicChannelID],
        include_locale: bool=False,
    ):
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
        cursor: Optional[str]=None,
        exclude_archived: bool=True,
        exclude_members: bool=True,
        limit: int=0,
    ):
        """https://api.slack.com/methods/channels.list"""

        params = {
            'exclude_archived': bool2str(exclude_archived),
            'exclude_members': bool2str(exclude_members),
            'limit': str(limit),
        }
        if cursor:
            params['cursor'] = cursor

        return await self._call('list', params)
