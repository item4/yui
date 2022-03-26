import pytest

from yui.api.encoder import bool2str
from yui.types.slack.attachment import Attachment
from yui.types.slack.attachment import Field
from yui.types.slack.block import Divider


@pytest.mark.asyncio
async def test_slack_api_chat_delete(bot):
    channel_id = 'C1234'

    ts = '1234.56'
    alternative_token = '1234567890'

    await bot.api.chat.delete(channel_id, ts, False)

    call = bot.call_queue.pop()
    assert call.method == 'chat.delete'
    assert call.data == {
        'channel': channel_id,
        'ts': ts,
        'as_user': bool2str(False),
    }
    assert call.token is None

    await bot.api.chat.delete(channel_id, ts, True, token=alternative_token)

    call = bot.call_queue.pop()
    assert call.method == 'chat.delete'
    assert call.data == {
        'channel': channel_id,
        'ts': ts,
        'as_user': bool2str(True),
    }
    assert call.token == alternative_token


@pytest.mark.asyncio
async def test_slack_api_chat_post_ephemeral(bot):
    channel_id = 'C1234'
    user_id = 'U5555'
    attachments = [
        Attachment(
            fallback='fallback val',
            title='title val',
            fields=[Field('field title1', 'field value1', False)],
        )
    ]
    blocks = [Divider()]
    text = 'text val'
    parse = 'text'
    username = 'strea'
    icon_url = (
        'https://item4.github.io/static/images/favicon/apple-icon-57x57.png'
    )
    icon_emoji = ':cake:'
    thread_ts = '12.34'

    with pytest.raises(TypeError):
        await bot.api.chat.postEphemeral(channel=channel_id, user=user_id)

    await bot.api.chat.postEphemeral(
        channel=channel_id,
        user=user_id,
        text=text,
    )

    call = bot.call_queue.pop()
    assert call.method == 'chat.postEphemeral'
    assert call.data == {
        'channel': channel_id,
        'user': user_id,
        'text': text,
    }
    assert call.json_mode

    await bot.api.chat.postEphemeral(
        channel=channel_id,
        user=user_id,
        attachments=attachments,
    )

    call = bot.call_queue.pop()
    assert call.method == 'chat.postEphemeral'
    assert call.data == {
        'channel': channel_id,
        'user': user_id,
        'attachments': [
            {
                'fallback': 'fallback val',
                'title': 'title val',
                'fields': [
                    {
                        'title': 'field title1',
                        'value': 'field value1',
                        'short': False,
                    },
                ],
            },
        ],
    }
    assert call.json_mode

    await bot.api.chat.postEphemeral(
        as_user=False,
        attachments=attachments,
        blocks=blocks,
        channel=channel_id,
        icon_emoji=icon_emoji,
        icon_url=icon_url,
        link_names=True,
        parse=parse,
        text=text,
        thread_ts=thread_ts,
        user=user_id,
        username=username,
        token='KIRITO',
    )

    call = bot.call_queue.pop()
    assert call.method == 'chat.postEphemeral'
    assert call.data == {
        'channel': channel_id,
        'user': user_id,
        'text': text,
        'parse': parse,
        'link_names': True,
        'attachments': [
            {
                'fallback': 'fallback val',
                'title': 'title val',
                'fields': [
                    {
                        'title': 'field title1',
                        'value': 'field value1',
                        'short': False,
                    },
                ],
            },
        ],
        'blocks': [{'type': 'divider'}],
        'username': username,
        'as_user': False,
        'icon_url': icon_url,
        'icon_emoji': icon_emoji,
        'thread_ts': thread_ts,
    }
    assert call.json_mode
    assert call.token == 'KIRITO'


@pytest.mark.asyncio
async def test_slack_api_chat_post_message(bot):
    channel_id = 'C1234'
    attachments = [
        Attachment(
            fallback='fallback val',
            title='title val',
            fields=[Field('field title1', 'field value1', False)],
        )
    ]
    blocks = [Divider()]
    text = 'text val'
    parse = 'text'
    username = 'strea'
    icon_url = (
        'https://item4.github.io/static/images/favicon/apple-icon-57x57.png'
    )
    icon_emoji = ':cake:'
    thread_ts = '12.34'
    mrkdwn = False

    with pytest.raises(TypeError):
        await bot.api.chat.postMessage(channel=channel_id)

    await bot.api.chat.postMessage(channel=channel_id, text=text, as_user=True)

    call = bot.call_queue.pop()
    assert call.method == 'chat.postMessage'
    assert call.data == {
        'channel': channel_id,
        'text': text,
        'as_user': True,
        'mrkdwn': True,
    }
    assert call.json_mode

    await bot.api.chat.postMessage(channel=channel_id, attachments=attachments)

    call = bot.call_queue.pop()
    assert call.method == 'chat.postMessage'
    assert call.data == {
        'channel': channel_id,
        'attachments': [
            {
                'fallback': 'fallback val',
                'title': 'title val',
                'fields': [
                    {
                        'title': 'field title1',
                        'value': 'field value1',
                        'short': False,
                    },
                ],
            },
        ],
        'mrkdwn': True,
    }
    assert call.json_mode

    await bot.api.chat.postMessage(
        as_user=False,
        attachments=attachments,
        blocks=blocks,
        channel=channel_id,
        icon_emoji=icon_emoji,
        icon_url=icon_url,
        link_names=True,
        mrkdwn=mrkdwn,
        parse=parse,
        reply_broadcast=True,
        text=text,
        thread_ts=thread_ts,
        unfurl_links=False,
        unfurl_media=True,
        username=username,
        token='KIRITO',
    )

    call = bot.call_queue.pop()
    assert call.method == 'chat.postMessage'
    assert call.data == {
        'channel': channel_id,
        'text': text,
        'parse': parse,
        'link_names': True,
        'attachments': [
            {
                'fallback': 'fallback val',
                'title': 'title val',
                'fields': [
                    {
                        'title': 'field title1',
                        'value': 'field value1',
                        'short': False,
                    },
                ],
            },
        ],
        'blocks': [{'type': 'divider'}],
        'unfurl_links': False,
        'unfurl_media': True,
        'username': username,
        'as_user': False,
        'icon_url': icon_url,
        'icon_emoji': icon_emoji,
        'thread_ts': thread_ts,
        'reply_broadcast': True,
        'mrkdwn': mrkdwn,
    }
    assert call.json_mode
    assert call.token == 'KIRITO'
