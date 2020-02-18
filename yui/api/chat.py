from typing import Any, Dict, List, Optional, Union

from .encoder import bool2str
from .endpoint import Endpoint
from ..types.base import ChannelID, Ts
from ..types.channel import Channel
from ..types.slack.attachment import Attachment
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

    async def postMessage(
        self,
        channel: Union[Channel, User, ChannelID],
        text: Optional[str] = None,
        parse=None,
        link_names: Optional[bool] = None,
        attachments: Optional[List[Attachment]] = None,
        unfurl_links: Optional[bool] = None,
        unfurl_media: Optional[bool] = None,
        username: Optional[str] = None,
        as_user: Optional[bool] = None,
        icon_url: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        thread_ts: Optional[Ts] = None,
        reply_broadcast: Optional[bool] = None,
        response_type: Optional[str] = None,
        replace_original: Optional[bool] = None,
        delete_original: Optional[bool] = None,
        *,
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

        if text is None and attachments is None:
            raise TypeError('text or attachement is required.')

        if text is not None:
            params['text'] = text

        if parse is not None:
            params['parse'] = parse

        if link_names is not None:
            params['link_names'] = link_names

        if attachments is not None:
            params['attachments'] = attachments

        if unfurl_links is not None:
            params['unfurl_links'] = unfurl_links

        if unfurl_media is not None:
            params['unfurl_media'] = unfurl_media

        if username is not None:
            params['username'] = username

        if as_user is not None:
            params['as_user'] = as_user

        if icon_url is not None:
            params['icon_url'] = icon_url

        if icon_emoji is not None:
            params['icon_emoji'] = icon_emoji

        if thread_ts is not None:
            params['thread_ts'] = thread_ts

        if reply_broadcast is not None:
            params['reply_broadcast'] = reply_broadcast

        if response_type in ('in_channel', 'ephemeral'):
            params['response_type'] = response_type

        if replace_original is not None:
            params['replace_original'] = replace_original

        if delete_original is not None:
            params['delete_original'] = delete_original

        return await self._call(
            'postMessage',
            params,
            token=token,
            json_mode=True,
        )
