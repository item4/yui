from yui.api.type import Action, Attachment, Confirmation, Field, OptionField


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
    assert attach.actions == None
    assert str(attach) == f"Attachment(title='{title}')"

    attach.add_field('field3', '3')

    assert len(attach.fields) == 3
    assert attach.fields[0].title == 'field1'
    assert attach.fields[1].title == 'field2'
    assert attach.fields[2].title == 'field3'


def test_action_class(): 
    id = None
    confirm = [Confirmation(
        dismiss_text='dismiss',
        ok_text='ok',
        text='some text',
        title='some title',
    )]
    data_source = 'data_source'
    min_query_length = 100
    name = 'Test Button'
    options = []
    selected_options = [OptionField(
        text='text',
        value='value',
        description='some description',
    )]
    style = 'text-align: center'
    text = 'Test Text'
    type = 'Some Type'
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
        url=url
    )

    assert action.id == id
    assert len(action.confirm) == len(confirm)
    assert action.data_source == action.data_source
    assert action.min_query_length == min_query_length
    assert action.name == name
    assert action.options == options
    assert len(action.selected_options) == len(1)
    assert action.selected_options[0].text == selected_options[0].text
    assert action.style == style
    assert action.text == text
    assert action.type ==  type
    assert action.value == value
    assert action.url == url

