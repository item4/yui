import json

from .type import Attachment, Field
from ..type import ChannelFromConfig, ChannelsFromConfig

__all__ = 'SlackEncoder',


def bool2str(value: bool) -> str:
    """Return bool as str."""

    if value:
        return '1'
    return '0'


class SlackEncoder(json.JSONEncoder):
    """JSON Encoder for slack"""

    def default(self, o):
        if isinstance(o, Field):
            return {
                'title': o.title,
                'value': o.value,
                'short': bool2str(o.short),
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
        elif isinstance(o, (ChannelFromConfig, ChannelsFromConfig)):
            raise TypeError('can not encode this type')
        return json.JSONEncoder.default(self, o)
