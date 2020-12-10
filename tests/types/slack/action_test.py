from yui.types.slack.action import Action
from yui.types.slack.action import ActionDataSource
from yui.types.slack.action import ActionStyle
from yui.types.slack.action import ActionType
from yui.types.slack.action import Confirmation
from yui.types.slack.action import OptionField
from yui.types.slack.action import OptionFieldGroup


def test_action_class():
    id = None
    confirm = Confirmation(
        dismiss_text='dismiss',
        ok_text='ok',
        text='some text',
        title='some title',
    )
    data_source = 'default'
    min_query_length = 100
    name = 'Test Button'
    options = [
        OptionField(
            text='test',
            value='test',
        )
    ]
    selected_options = [
        OptionField(
            text='text',
            value='value',
            description='some description',
        )
    ]
    style = 'danger'
    text = 'Test Text'
    type = 'button'
    value = ''
    url = 'https://item4.github.io'

    action = Action(
        id=id,
        confirm=confirm,
        data_source=data_source,
        min_query_length=min_query_length,
        name=name,
        options=options,
        selected_options=selected_options,
        style=style,
        text=text,
        type=type,
        value=value,
        url=url,
    )

    assert action.id == id
    assert action.confirm == confirm
    assert action.data_source == ActionDataSource(data_source)
    assert action.min_query_length is None
    assert action.name == name
    assert action.options == options
    assert action.selected_options == selected_options
    assert action.style == ActionStyle(style)
    assert action.text == text
    assert action.type == ActionType(type)
    assert action.value == value
    assert action.url == url

    action = Action(
        name=name,
        text=text,
        type=type,
        options=[
            OptionField(
                text='test',
                value='test',
            )
        ],
        option_groups=[
            OptionFieldGroup(
                text='text',
                options=[OptionField(text='test2', value='test2')],
            )
        ],
    )

    assert action.options is None
    assert action.option_groups == [
        OptionFieldGroup(
            text='text', options=[OptionField(text='test2', value='test2')]
        ),
    ]
