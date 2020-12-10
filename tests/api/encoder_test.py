from yui.api.encoder import bool2str
from yui.api.encoder import to_json
from yui.types.slack.action import Action
from yui.types.slack.action import Confirmation
from yui.types.slack.action import OptionField
from yui.types.slack.action import OptionFieldGroup
from yui.types.slack.attachment import Attachment
from yui.types.slack.attachment import Field
from yui.utils import json


def test_bool2str():
    assert bool2str(True) == '1'
    assert bool2str(False) == '0'


def to_test_type(o):
    return json.loads(to_json(o))


def test_to_json():
    field = to_test_type(Field('title val', 'value val', True))
    assert field == {
        'title': 'title val',
        'value': 'value val',
        'short': '1',
    }

    attachment = to_test_type(
        Attachment(
            fallback='fallback val',
            title='title val',
            fields=[Field('field title1', 'field value1', False)],
            actions=[
                Action(
                    name='action1 name',
                    text='action1 text',
                    type='button',
                    data_source='external',
                    options=[
                        OptionField(text='a1 o1 text', value='a1 o1 value')
                    ],
                    style='danger',
                    min_query_length=100,
                    confirm=Confirmation(text='confirm text'),
                    selected_options=[
                        OptionField(
                            text='a1 so1 text',
                            value='a1 so1 value',
                        )
                    ],
                    value='action1 value',
                    url='action1 url',
                ),
                Action(
                    name='action2 name',
                    text='action2 text',
                    type='select',
                    option_groups=[
                        OptionFieldGroup(
                            text='a2 og1 text',
                            options=[
                                OptionField(
                                    text='a2 og1 o1 text',
                                    value='a2 og1 o1 value',
                                ),
                            ],
                        )
                    ],
                ),
            ],
        )
    )
    assert attachment == {
        'fallback': 'fallback val',
        'title': 'title val',
        'fields': [
            {'title': 'field title1', 'value': 'field value1', 'short': '0'}
        ],
        'actions': [
            {
                'name': 'action1 name',
                'text': 'action1 text',
                'type': 'button',
                'data_source': 'external',
                'options': [{'text': 'a1 o1 text', 'value': 'a1 o1 value'}],
                'style': 'danger',
                'min_query_length': 100,
                'confirm': {'text': 'confirm text'},
                'selected_options': [
                    {'text': 'a1 so1 text', 'value': 'a1 so1 value'},
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
            },
        ],
    }
