from yui.types.slack.attachment import Attachment, Field


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
        ts=ts,
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
