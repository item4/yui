import json
import typing

from attrdict import AttrDict

from .util import bool2str


__all__ = 'SlackAPI',


class Field:
    """Field on Attachment"""

    def __init__(self, title: str, value: str, short: bool):
        """Initialize"""

        self.title = title
        self.value = value
        self.short = short


class Attachment:
    """Slack Attachment"""

    def __init__(
        self,
        *,
        fallback: str=None,
        color: str=None,
        pretext: str=None,
        author_name: str=None,
        author_link: str=None,
        author_icon: str=None,
        title: str=None,
        title_link: str=None,
        text: str=None,
        fields: typing.List[Field]=None,
        image_url: str=None,
        thumb_url: str=None,
        footer: str=None,
        footer_icon: str=None,
        ts: int=None
    ):
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

    def add_field(self, title: str, value: str, short: bool=False):
        self.fields.append(Field(title, value, short))


class SlackAPI:
    """API Interface"""

    def __init__(self, bot):
        """Initialize"""

        self.bot = bot

        self.chat = AttrDict()
        self.chat.postMessage = self.chat_post_message

        self.users = AttrDict()
        self.users.info = self.users_info

    async def chat_post_message(
        self,
        channel: str,
        text: str=None,
        parse=None,
        link_names: bool=None,
        attachments: typing.List[Attachment]=None,
        unfurl_links: bool=None,
        unfurl_media: bool=None,
        username: str=None,
        as_user: bool=None,
        icon_url: str=None,
        icon_emoji: str=None,
        thread_ts: str=None,
        reply_broadcast: bool=None,
    ):
        """https://api.slack.com/methods/chat.postMessage"""

        param = {
            'channel': channel,
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
            param['attachments'] = json.dumps(attachments, cls=SlackEncoder)

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

    async def users_info(self, user: str):
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
        if isinstance(o, bool):
            return bool2str(o)
        elif isinstance(o, Field):
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
