import json

import pytest

from yui.api import Attachment, Field, SlackEncoder

from .util import FakeBot


def test_field_class():
    TITLE = 'Test title for pytest'
    VALUE = '123'
    field = Field(title=TITLE, value=VALUE, short=True)

    assert field.title == TITLE
    assert field.value == VALUE
    assert field.short
    assert str(field) == f"Field('{TITLE}', '{VALUE}', True)"


def test_attachment_class():
    FALLBACK = 'fallback'
    COLOR = 'black'
    PRETEXT = 'pretext'
    AUTHOR_NAME = 'item4'
    AUTHOR_LINK = 'https://item4.github.io/'
    AUTHOR_ICON = 'https://item4.github.io/static/images/item4.png'
    TITLE = 'title'
    TEXT = 'text'
    FIELDS = [Field('field1', '1', False), Field('field2', '2', True)]
    IMAGE_URL = (
        'https://item4.github.io/static/images/favicon/apple-icon-60x60.png'
    )
    THUMB_URL = (
        'https://item4.github.io/static/images/favicon/apple-icon-57x57.png'
    )
    FOOTER = 'footer'
    FOOTER_ICON = (
        'https://item4.github.io/static/images/favicon/apple-icon-72x72.png'
    )
    TS = 123456
    attach = Attachment(
        fallback=FALLBACK,
        color=COLOR,
        pretext=PRETEXT,
        author_name=AUTHOR_NAME,
        author_link=AUTHOR_LINK,
        author_icon=AUTHOR_ICON,
        title=TITLE,
        text=TEXT,
        fields=FIELDS,
        image_url=IMAGE_URL,
        thumb_url=THUMB_URL,
        footer=FOOTER,
        footer_icon=FOOTER_ICON,
        ts=TS
    )

    assert attach.fallback == FALLBACK
    assert attach.color == COLOR
    assert attach.pretext == PRETEXT
    assert attach.author_name == AUTHOR_NAME
    assert attach.author_link == AUTHOR_LINK
    assert attach.author_icon == AUTHOR_ICON
    assert attach.title == TITLE
    assert attach.text == TEXT
    assert len(attach.fields) == 2
    assert attach.fields[0].title == 'field1'
    assert attach.fields[1].title == 'field2'
    assert attach.image_url == IMAGE_URL
    assert attach.thumb_url == THUMB_URL
    assert attach.footer == FOOTER
    assert attach.footer_icon == FOOTER_ICON
    assert attach.ts == TS
    assert str(attach) == f"Attachment(title='{TITLE}')"

    attach.add_field('field3', '3')

    assert len(attach.fields) == 3
    assert attach.fields[0].title == 'field1'
    assert attach.fields[1].title == 'field2'
    assert attach.fields[2].title == 'field3'


def test_slack_encoder_class():
    def dumps(o):
        return json.dumps(o, cls=SlackEncoder, separators=(',', ':'))

    assert dumps(Field('title val', 'value val', True)) == (
        '{"title":"title val","value":"value val","short":true}'
    )
    assert dumps(Attachment(
        fallback='fallback val',
        title='title val',
        fields=[Field('field title1', 'field value1', False)],
    )) == (
        '{"fallback":"fallback val","title":"title val","fields":'
        '[{"title":"field title1","value":"field value1","short":false}]}'
    )

    class Dummy:
        pass

    with pytest.raises(TypeError):
        dumps(Dummy())


@pytest.mark.asyncio
async def test_slack_api_channels_info():
    channel = 'C1234'

    bot = FakeBot()

    await bot.api.channels.info(channel)

    call = bot.call_queue.pop()
    assert call.method == 'channels.info'
    assert call.data == {'channel': channel}


@pytest.mark.asyncio
async def test_slack_api_chat_post_message():
    channel = 'C1234'
    attachments = [Attachment(
        fallback='fallback val',
        title='title val',
        fields=[Field('field title1', 'field value1', False)],
    )]
    text = 'text val'
    parse = 'text'
    username = 'strea'
    icon_url = (
        'https://item4.github.io/static/images/favicon/apple-icon-57x57.png'
    )
    icon_emoji = ':cake:'
    thread_ts = '12.34'

    bot = FakeBot()

    with pytest.raises(TypeError):
        await bot.api.chat.postMessage(channel=channel)

    await bot.api.chat.postMessage(channel=channel, text=text, as_user=True)

    call = bot.call_queue.pop()
    assert call.method == 'chat.postMessage'
    assert call.data == {'channel': channel, 'text': text, 'as_user': 'true'}

    await bot.api.chat.postMessage(channel=channel, attachments=attachments)

    call = bot.call_queue.pop()
    assert call.method == 'chat.postMessage'
    assert call.data == {
        'channel': channel,
        'attachments': ('[{"fallback":"fallback val","title":"title val",'
                        '"fields":[{"title":"field title1",'
                        '"value":"field value1","short":false}]}]'),
    }

    await bot.api.chat.postMessage(
        channel=channel,
        text=text,
        parse=parse,
        link_names=True,
        attachments=attachments,
        unfurl_links=False,
        unfurl_media=True,
        username=username,
        as_user=False,
        icon_url=icon_url,
        icon_emoji=icon_emoji,
        thread_ts=thread_ts,
        reply_broadcast=True,
    )

    call = bot.call_queue.pop()
    assert call.method == 'chat.postMessage'
    assert call.data == {
        'channel': channel,
        'text': text,
        'parse': parse,
        'link_names': 'true',
        'attachments': ('[{"fallback":"fallback val","title":"title val",'
                        '"fields":[{"title":"field title1",'
                        '"value":"field value1","short":false}]}]'),
        'unfurl_links': 'false',
        'unfurl_media': 'true',
        'username': username,
        'as_user': 'false',
        'icon_url': icon_url,
        'icon_emoji': icon_emoji,
        'thread_ts': thread_ts,
        'reply_broadcast': 'true',
    }


@pytest.mark.asyncio
async def test_slack_api_users_info():
    user = 'U1234'

    bot = FakeBot()

    await bot.api.users.info(user)

    call = bot.call_queue.pop()
    assert call.method == 'users.info'
    assert call.data == {'user': user}
