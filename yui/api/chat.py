from typing import Any, Dict, List, Optional, Union

from .encoder import bool2str
from .endpoint import Endpoint
from ..types.base import ChannelID, Ts, UserID
from ..types.channel import Channel
from ..types.slack.attachment import Attachment
from ..types.slack.block import Block
from ..types.slack.response import APIResponse
from ..types.user import User


class Chat(Endpoint):

    name = 'chat'

    async def delete(
        self,
        channel: Union[Channel, ChannelID],
        ts: Ts,
        as_user: Optional[bool] = None,
        *,
        token: Optional[str] = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/chat.delete"""

        if isinstance(channel, Channel):
            channel_id = channel.id
        else:
            channel_id = channel

        params = {
            'channel': channel_id,
            'ts': ts,
        }

        if as_user is not None:
            params['as_user'] = bool2str(as_user)

        return await self._call('delete', params, token=token)

    async def postEphemeral(
        self,
        channel: Union[Channel, User, ChannelID],
        user: Union[User, UserID],
        text: Optional[str] = None,
        *,
        attachments: Optional[List[Attachment]] = None,
        as_user: Optional[bool] = None,
        blocks: Optional[List[Block]] = None,
        icon_emoji: Optional[str] = None,
        icon_url: Optional[str] = None,
        link_names: Optional[bool] = None,
        parse: Optional[str] = None,
        thread_ts: Optional[Ts] = None,
        username: Optional[str] = None,
        token: Optional[str] = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/chat.postEphemeral"""

        if isinstance(channel, (Channel, User)):
            channel_id = channel.id
        else:
            channel_id = channel

        if isinstance(user, User):
            user_id = user.id
        else:
            user_id = user

        params: Dict[str, Any] = {
            'channel': channel_id,
            'user': user_id,
        }

        if text is None and blocks is None and attachments is None:
            raise TypeError('text or attachement or blocks is required.')

        if text is not None:
            params['text'] = text

        if attachments is not None:
            params['attachments'] = attachments

        if as_user is not None:
            params['as_user'] = as_user

        if blocks is not None:
            params['blocks'] = blocks

        if icon_emoji is not None:
            params['icon_emoji'] = icon_emoji

        if icon_url is not None:
            params['icon_url'] = icon_url

        if link_names is not None:
            params['link_names'] = link_names

        if parse is not None:
            params['parse'] = parse

        if thread_ts is not None:
            params['thread_ts'] = thread_ts

        if username is not None:
            params['username'] = username

        return await self._call(
            'postEphemeral',
            params,
            token=token,
            json_mode=True,
        )

    async def postMessage(
        self,
        channel: Union[Channel, User, ChannelID],
        text: Optional[str] = None,
        *,
        as_user: Optional[bool] = None,
        attachments: Optional[List[Attachment]] = None,
        blocks: Optional[List[Block]] = None,
        icon_emoji: Optional[str] = None,
        icon_url: Optional[str] = None,
        link_names: Optional[bool] = None,
        mrkdwn: bool = True,
        parse: Optional[str] = None,
        reply_broadcast: Optional[bool] = None,
        thread_ts: Optional[Ts] = None,
        unfurl_links: Optional[bool] = None,
        unfurl_media: Optional[bool] = None,
        username: Optional[str] = None,
        token: Optional[str] = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/chat.postMessage"""

        if isinstance(channel, (Channel, User)):
            channel_id = channel.id
        else:
            channel_id = channel

        params: Dict[str, Any] = {
            'channel': channel_id,
        }

        if text is None and blocks is None and attachments is None:
            raise TypeError('text or attachement or blocks is required.')

        if text is not None:
            params['text'] = text

        if as_user is not None:
            params['as_user'] = as_user

        if attachments is not None:
            params['attachments'] = attachments

        if blocks is not None:
            params['blocks'] = blocks

        if icon_emoji is not None:
            params['icon_emoji'] = icon_emoji

        if icon_url is not None:
            params['icon_url'] = icon_url

        if link_names is not None:
            params['link_names'] = link_names

        if mrkdwn is not None:
            params['mrkdwn'] = mrkdwn

        if parse is not None:
            params['parse'] = parse

        if reply_broadcast is not None:
            params['reply_broadcast'] = reply_broadcast

        if thread_ts is not None:
            params['thread_ts'] = thread_ts

        if unfurl_links is not None:
            params['unfurl_links'] = unfurl_links

        if unfurl_media is not None:
            params['unfurl_media'] = unfurl_media

        if username is not None:
            params['username'] = username

        return await self._call(
            'postMessage',
            params,
            token=token,
            json_mode=True,
        )
