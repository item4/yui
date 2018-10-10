from yui.api.type import (
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


def test_field_class():
    title = 'Test title for pytest'
    value = '123'
    field = Field(title=title, value=value, short=True)

    assert field.title == title
    assert field.value == value
    assert field.short


def test_attachment_class():
    fallback = 'fallback'
    color = 'black'
    pretext = 'pretext'
    author_name = 'item4'
    author_link = 'https://item4.github.io/'
    author_icon = 'https://item4.github.io/static/images/item4.png'
    title = 'title'
    text = 'text'
    fields = [Field('field1', '1', False), Field('field2', '2', True)]
    image_url = (
        'https://item4.github.io/static/images/favicon/apple-icon-60x60.png'
    )
    thumb_url = (
        'https://item4.github.io/static/images/favicon/apple-icon-57x57.png'
    )
    footer = 'footer'
    footer_icon = (
        'https://item4.github.io/static/images/favicon/apple-icon-72x72.png'
    )
    ts = 123456
    attach = Attachment(
        fallback=fallback,
        color=color,
        pretext=pretext,
        author_name=author_name,
        author_link=author_link,
        author_icon=author_icon,
        title=title,
        text=text,
        fields=fields,
        image_url=image_url,
        thumb_url=thumb_url,
        footer=footer,
        footer_icon=footer_icon,
        ts=ts
    )

    assert attach.fallback == fallback
    assert attach.color == color
    assert attach.pretext == pretext
    assert attach.author_name == author_name
    assert attach.author_link == author_link
    assert attach.author_icon == author_icon
    assert attach.title == title
    assert attach.text == text
    assert len(attach.fields) == 2
    assert attach.fields[0].title == 'field1'
    assert attach.fields[1].title == 'field2'
    assert attach.image_url == image_url
    assert attach.thumb_url == thumb_url
    assert attach.footer == footer
    assert attach.footer_icon == footer_icon
    assert attach.ts == ts
    assert attach.actions is None


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
    options = [OptionField(
        text='test',
        value='test',
    )]
    selected_options = [OptionField(
        text='text',
        value='value',
        description='some description',
    )]
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
        options=[OptionField(
            text='test',
            value='test',
        )],
        option_groups=[OptionGroup(text='text', options=[
            OptionField(
                text='test2',
                value='test2',
            ),
        ])],
    )

    assert action.options is None
    assert action.option_groups == [
        OptionGroup(text='text', options=[
            OptionField(
                text='test2',
                value='test2',
            ),
        ]),
    ]
