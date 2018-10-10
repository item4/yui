import json

from .type import (
    Action,
    ActionDataSource,
    ActionStyle,
    ActionType,
    Attachment,
    Confirmation,
    Field,
    OptionField,
    OptionGroup,
)
from ..type import ChannelFromConfig, ChannelsFromConfig

__all__ = 'SlackEncoder', 'bool2str', 'remove_none'


def bool2str(value: bool) -> str:
    """Return bool as str."""

    if value:
        return '1'
    return '0'


def remove_none(data):
    return {k: v for k, v in data.items() if v is not None}


class SlackEncoder(json.JSONEncoder):
    """JSON Encoder for slack"""

    def default(self, o):
        if isinstance(o, Field):
            return {
                'title': o.title,
                'value': o.value,
                'short': bool2str(o.short),
            }
        elif isinstance(o, (ActionDataSource, ActionStyle, ActionType)):
            return o.value
        elif isinstance(o, Confirmation):
            return remove_none({
                'dismiss_text': o.dismiss_text,
                'ok_text': o.ok_text,
                'text': o.text,
                'title': o.title,
            })
        elif isinstance(o, OptionField):
            return remove_none({
                'text': o.text,
                'value': o.value,
                'description': o.description,
            })
        elif isinstance(o, OptionGroup):
            return {
                'text': o.text,
                'options': o.options,
            }
        elif isinstance(o, Action):
            return remove_none({
                'name': o.name,
                'text': o.text,
                'type': o.type,
                'style': o.style,
                'data_source': o.data_source,
                'id': o.id,
                'confirm': o.confirm,
                'min_query_length': o.min_query_length,
                'options': o.options,
                'option_groups': o.option_groups,
                'selected_options': o.selected_options,
                'value': o.value,
                'url': o.url,
            })
        elif isinstance(o, Attachment):
            return remove_none({
                'fallback': o.fallback,
                'color': o.color,
                'pretext': o.pretext,
                'author_name': o.author_name,
                'author_link': o.author_link,
                'author_icon': o.author_icon,
                'title': o.title,
                'title_link': o.title_link,
                'text': o.text,
                'actions': o.actions,
                'fields': o.fields,
                'image_url': o.image_url,
                'thumb_url': o.thumb_url,
                'footer': o.footer,
                'footer_icon': o.footer_icon,
                'ts': o.ts,
            })
        elif isinstance(o, (ChannelFromConfig, ChannelsFromConfig)):
            raise TypeError('can not encode this type')
        return json.JSONEncoder.default(self, o)
