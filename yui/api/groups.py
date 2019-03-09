from typing import Union

from .encoder import bool2str
from .endpoint import Endpoint
from .type import APIResponse
from ..types.base import PrivateChannelID
from ..types.channel import PrivateChannel


class Groups(Endpoint):

    name = 'groups'

    async def info(
        self,
        channel: Union[PrivateChannel, PrivateChannelID],
        include_locale: bool = False,
    ) -> APIResponse:
        """https://api.slack.com/methods/groups.info"""

        if isinstance(channel, PrivateChannel):
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
        exclude_archived: bool = True,
        exclude_members: bool = True,
    ) -> APIResponse:
        """https://api.slack.com/methods/groups.list"""

        return await self._call(
            'list',
            {
                'exclude_archived': bool2str(exclude_archived),
                'exclude_members': bool2str(exclude_members),
            }
        )
