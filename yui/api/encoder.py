import json

from .type import Action, Attachment, Confirmation, Field, OptionField
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
        elif isinstance(o, Confirmation):
            return {k: v for k, v in {
                'dismiss_text': o.dismiss_text,
                'ok_text': o.ok_text,
                'text': o.text,
                'title': o.title,
            }.items() if v is not None}
        elif isinstance(o, OptionField):
            return {k: v for k, v in {
                'text': o.text,
                'value': o.value,
                'description': o.description,
            }.items() if v is not None}
        elif isinstance(o, Action):
            return {k: v for k, v in {
                'id': o.id,
                'confirm': o.confirm,
                'data_source': o.data_source,
                'min_query_length': o.min_query_length,
                'name': o.name,
                'options': o.options,
                'selected_options': o.selected_options,
                'style': o.style,
                'text': o.text,
                'type': o.type,
                'value': o.value,
                'url': o.url,
            }.items() if v is not None}
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
