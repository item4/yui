import json

import pytest

from yui.api import Attachment, Field, SlackEncoder
from yui.type import PrivateChannel, PublicChannel

from .util import FakeBot


def test_field_class():
    title = 'Test title for pytest'
    value = '123'
    field = Field(title=title, value=value, short=True)

    assert field.title == title
    assert field.value == value
    assert field.short
    assert str(field) == f"Field('{title}', '{value}', True)"


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
    assert str(attach) == f"Attachment(title='{title}')"

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
    channel_id = 'C1234'
    channel = PublicChannel(id='C4567')

    bot = FakeBot()

    await bot.api.channels.info(channel_id)
    call = bot.call_queue.pop()
    assert call.method == 'channels.info'
    assert call.data == {
        'channel': channel_id,
        'include_locale': 'false',
    }

    await bot.api.channels.info(channel)
    call = bot.call_queue.pop()
    assert call.method == 'channels.info'
    assert call.data == {
        'channel': channel.id,
        'include_locale': 'false',
    }


@pytest.mark.asyncio
async def test_slack_api_channels_list():
    cursor = '1234asdf'
    exclude_archived = False
    exclude_members = False
    limit = 12

    bot = FakeBot()

    await bot.api.channels.list(
        cursor,
        exclude_archived,
        exclude_members,
        limit
    )
    call = bot.call_queue.pop()
    assert call.method == 'channels.list'
    assert call.data == {
        'cursor': cursor,
        'exclude_archived': 'false',
        'exclude_members': 'false',
        'limit': '12',
    }


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
async def test_slack_api_groups_info():
    group_id = 'G1'
    group = PrivateChannel(id='G2', name='secret')

    bot = FakeBot()

    await bot.api.groups.info(group_id)
    call = bot.call_queue.pop()
    assert call.method == 'groups.info'
    assert call.data == {
        'channel': 'G1',
        'include_locale': 'false',
    }

    await bot.api.groups.info(group)
    call = bot.call_queue.pop()
    assert call.method == 'groups.info'
    assert call.data == {
        'channel': 'G2',
        'include_locale': 'false',
    }


@pytest.mark.asyncio
async def test_slack_api_groups_list():
    bot = FakeBot()

    await bot.api.groups.list()
    call = bot.call_queue.pop()
    assert call.method == 'groups.list'
    assert call.data == {
        'exclude_archived': 'true',
        'exclude_members': 'true',
    }


@pytest.mark.asyncio
async def test_slack_api_im_list():
    bot = FakeBot()

    await bot.api.im.list(cursor='asdf', limit=10)
    call = bot.call_queue.pop()
    assert call.method == 'im.list'
    assert call.data == {
        'cursor': 'asdf',
        'limit': '10',
    }


@pytest.mark.asyncio
async def test_slack_api_users_info():
    user = 'U1234'

    bot = FakeBot()

    await bot.api.users.info(user)

    call = bot.call_queue.pop()
    assert call.method == 'users.info'
    assert call.data == {'user': user}
