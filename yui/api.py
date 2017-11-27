import json
from typing import Dict, List, Optional, Union

from attrdict import AttrDict

from .type import (
    Channel,
    ChannelID,
    PrivateChannel,
    PrivateChannelID,
    PublicChannel,
    PublicChannelID,
    Ts,
    UserID,
)
from .util import bool2str


__all__ = 'Attachment', 'Field', 'SlackAPI', 'SlackEncoder'


class Field:
    """Field on Attachment"""

    def __init__(self, title: str, value: str, short: bool) -> None:
        """Initialize"""

        self.title = title
        self.value = value
        self.short = short

    def __str__(self) -> str:
        return f'Field({self.title!r}, {self.value!r}, {self.short!r})'


class Attachment:
    """Slack Attachment"""

    def __init__(
        self,
        *,
        fallback: Optional[str]=None,
        color: Optional[str]=None,
        pretext: Optional[str]=None,
        author_name: Optional[str]=None,
        author_link: Optional[str]=None,
        author_icon: Optional[str]=None,
        title: Optional[str]=None,
        title_link: Optional[str]=None,
        text: Optional[str]=None,
        fields: Optional[List[Field]]=None,
        image_url: Optional[str]=None,
        thumb_url: Optional[str]=None,
        footer: Optional[str]=None,
        footer_icon: Optional[str]=None,
        ts: Optional[int]=None
    ) -> None:
        """Initialize"""

        self.fallback = fallback
        self.color = color
        self.pretext = pretext
        self.author_name = author_name
        self.author_link = author_link
        self.author_icon = author_icon
        self.title = title
        self.title_link = title_link
        self.text = text
        self.fields = fields if fields else []
        self.image_url = image_url
        self.thumb_url = thumb_url
        self.footer = footer
        self.footer_icon = footer_icon
        self.ts = ts

    def add_field(self, title: str, value: str, short: Optional[bool]=False):
        self.fields.append(Field(title, value, short))

    def __str__(self) -> str:
        return f'Attachment(title={self.title!r})'


class SlackAPI:
    """API Interface"""

    def __init__(self, bot):
        """Initialize"""

        self.bot = bot

        self.channels = AttrDict()
        self.channels.info = self.channels_info
        self.channels.list = self.channels_list

        self.chat = AttrDict()
        self.chat.postMessage = self.chat_post_message

        self.groups = AttrDict()
        self.groups.info = self.groups_info
        self.groups.list = self.groups_list

        self.im = AttrDict()
        self.im.list = self.im_list

        self.users = AttrDict()
        self.users.info = self.users_info

    async def channels_info(
        self,
        channel: Union[PublicChannel, PublicChannelID],
        include_locale: bool=False,
    ):
        """https://api.slack.com/methods/channels.info"""

        if isinstance(channel, PublicChannel):
            channel_id = channel.id
        else:
            channel_id = channel

        return await self.bot.call(
            'channels.info',
            {
                'channel': channel_id,
                'include_locale': bool2str(include_locale),
            }
        )

    async def channels_list(
        self,
        cursor: Optional[str]=None,
        exclude_archived: bool=True,
        exclude_members: bool=True,
        limit: int=0,
    ):
        """https://api.slack.com/methods/channels.list"""

        param = {
            'exclude_archived': bool2str(exclude_archived),
            'exclude_members': bool2str(exclude_members),
            'limit': str(limit),
        }
        if cursor:
            param['cursor'] = cursor

        return await self.bot.call('channels.list', param)

    async def chat_post_message(
        self,
        channel: Union[Channel, ChannelID],
        text: Optional[str]=None,
        parse=None,
        link_names: Optional[bool]=None,
        attachments: Optional[List[Attachment]]=None,
        unfurl_links: Optional[bool]=None,
        unfurl_media: Optional[bool]=None,
        username: Optional[str]=None,
        as_user: Optional[bool]=None,
        icon_url: Optional[str]=None,
        icon_emoji: Optional[str]=None,
        thread_ts: Optional[Ts]=None,
        reply_broadcast: Optional[bool]=None,
    ):
        """https://api.slack.com/methods/chat.postMessage"""

        if isinstance(channel, Channel):
            channel_id = channel.id
        else:
            channel_id = channel

        param: Dict[str, str] = {
            'channel': channel_id,
        }

        if text is None and attachments is None:
            raise TypeError('text or attachement is required.')

        if text is not None:
            param['text'] = text

        if parse is not None:
            param['parse'] = parse

        if link_names is not None:
            param['link_names'] = bool2str(link_names)

        if attachments is not None:
            param['attachments'] = json.dumps(
                attachments,
                cls=SlackEncoder,
                separators=(',', ':'),
            )

        if unfurl_links is not None:
            param['unfurl_links'] = bool2str(unfurl_links)

        if unfurl_media is not None:
            param['unfurl_media'] = bool2str(unfurl_media)

        if username is not None:
            param['username'] = username

        if as_user is not None:
            param['as_user'] = bool2str(as_user)

        if icon_url is not None:
            param['icon_url'] = icon_url

        if icon_emoji is not None:
            param['icon_emoji'] = icon_emoji

        if thread_ts is not None:
            param['thread_ts'] = thread_ts

        if reply_broadcast is not None:
            param['reply_broadcast'] = bool2str(reply_broadcast)

        return await self.bot.call('chat.postMessage', param)

    async def groups_info(
        self,
        channel: Union[PrivateChannel, PrivateChannelID],
        include_locale: bool=False,
    ):
        """https://api.slack.com/methods/groups.info"""

        if isinstance(channel, PrivateChannel):
            channel_id = channel.id
        else:
            channel_id = channel

        return await self.bot.call(
            'groups.info',
            {
                'channel': channel_id,
                'include_locale': bool2str(include_locale),
            }
        )

    async def groups_list(
        self,
        exclude_archived: bool=True,
        exclude_members: bool=True,
    ):
        """https://api.slack.com/methods/groups.list"""

        return await self.bot.call(
            'groups.list',
            {
                'exclude_archived': bool2str(exclude_archived),
                'exclude_members': bool2str(exclude_members),
            }
        )

    async def im_list(
        self,
        cursor: Optional[str]=None,
        limit: Optional[int]=None,
    ):
        """https://api.slack.com/methods/im.list"""

        param = {}
        if cursor:
            param['cursor'] = cursor
        if limit:
            param['limit'] = str(limit)

        return await self.bot.call('im.list', param)

    async def users_info(self, user: UserID):
        """https://api.slack.com/methods/users.info"""

        return await self.bot.call(
            'users.info',
            {
                'user': user,
            }
        )


class SlackEncoder(json.JSONEncoder):
    """JSON Encoder for slack"""

    def default(self, o):
        if isinstance(o, Field):
            return {
                'title': o.title,
                'value': o.value,
                'short': o.short,
            }
        elif isinstance(o, Attachment):
            return {k: v for k, v in {
                    'fallback': o.fallback,
                    'color': o.color,
                    'pretext': o.pretext,
                    'author_name': o.author_name,
                    'author_link': o.author_link,
                    'author_icon': o.author_icon,
                    'title': o.title,
                    'title_link': o.title_link,
                    'text': o.text,
                    'fields': o.fields,
                    'image_url': o.image_url,
                    'thumb_url': o.thumb_url,
                    'footer': o.footer,
                    'footer_icon': o.footer_icon,
                    'ts': o.ts,
                    }.items() if v is not None}
        return json.JSONEncoder.default(self, o)
