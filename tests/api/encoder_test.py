import json

import pytest

import ujson

from yui.api.encoder import SlackEncoder, bool2str, remove_none
from yui.api.type import (
    Action,
    Attachment,
    Confirmation,
    Field,
    OptionField,
    OptionGroup,
)
from yui.types.namespace.linked import ChannelFromConfig, ChannelsFromConfig


def test_bool2str():
    assert bool2str(True) == '1'
    assert bool2str(False) == '0'


def test_remove_none():
    assert remove_none({None: 1, 2: None, False: 3, 4: False}) == {
        None: 1,
        False: 3,
        4: False,
    }


def test_slack_encoder_class():
    def encode(o):
        return ujson.loads(
            json.dumps(o, cls=SlackEncoder, separators=(',', ':'))
        )

    field = encode(Field('title val', 'value val', True))
    assert field == {
        'title': 'title val',
        'value': 'value val',
        'short': '1',
    }

    attachment = encode(Attachment(
        fallback='fallback val',
        title='title val',
        fields=[Field('field title1', 'field value1', False)],
        actions=[
            Action(
                name='action1 name',
                text='action1 text',
                type='button',
                data_source='external',
                options=[OptionField(text='a1 o1 text', value='a1 o1 value')],
                style='danger',
                min_query_length=100,
                confirm=Confirmation(text='confirm text'),
                selected_options=[OptionField(
                    text='a1 so1 text',
                    value='a1 so1 value',
                )],
                value='action1 value',
                url='action1 url',
            ),
            Action(
                name='action2 name',
                text='action2 text',
                type='select',
                option_groups=[OptionGroup(
                    text='a2 og1 text',
                    options=[
                        OptionField(
                            text='a2 og1 o1 text',
                            value='a2 og1 o1 value',
                        ),
                    ],
                )],
            )
        ]
    ))
    assert attachment == {
        'fallback': 'fallback val',
        'title': 'title val',
        'fields': [{
            'title': 'field title1',
            'value': 'field value1',
            'short': '0',
        }],
        'actions': [
            {
                'name': 'action1 name',
                'text': 'action1 text',
                'type': 'button',
                'data_source': 'external',
                'options': [
                    {
                        'text': 'a1 o1 text',
                        'value': 'a1 o1 value',
                    },
                ],
                'style': 'danger',
                'min_query_length': 100,
                'confirm': {
                    'text': 'confirm text'
                },
                'selected_options': [
                    {
                        'text': 'a1 so1 text',
                        'value': 'a1 so1 value',
                    },
                ],
                'value': 'action1 value',
                'url': 'action1 url',
            },
            {
                'name': 'action2 name',
                'text': 'action2 text',
                'type': 'select',
                'option_groups': [
                    {
                        'text': 'a2 og1 text',
                        'options': [
                            {
                                'text': 'a2 og1 o1 text',
                                'value': 'a2 og1 o1 value',
                            },
                        ],
                    },
                ],
            }
        ],
    }

    class Dummy:
        pass

    with pytest.raises(TypeError):
        encode(Dummy())

    with pytest.raises(TypeError):
        encode(ChannelFromConfig('general'))

    with pytest.raises(TypeError):
        encode(ChannelsFromConfig('commons'))
