import pytest

from yui.api.encoder import bool2str
from yui.api.type import Attachment, Field

from ..util import FakeBot


@pytest.mark.asyncio
async def test_slack_api_chat_delete():
    bot = FakeBot()
    channel = bot.add_channel('C4567', 'test')
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

    await bot.api.chat.delete(channel, ts, True, token=alternative_token)

    call = bot.call_queue.pop()
    assert call.method == 'chat.delete'
    assert call.data == {
        'channel': channel.id,
        'ts': ts,
        'as_user': bool2str(True),
    }
    assert call.token == alternative_token


@pytest.mark.asyncio
async def test_slack_api_chat_post_message():
    bot = FakeBot()
    channel = bot.add_channel('C4567', 'test')
    channel_id = 'C1234'
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
    assert call.data == {
        'channel': channel.id,
        'text': text,
        'as_user': bool2str(True),
    }

    await bot.api.chat.postMessage(channel=channel_id, attachments=attachments)

    call = bot.call_queue.pop()
    assert call.method == 'chat.postMessage'
    assert call.data == {
        'channel': channel_id,
        'attachments': ('[{"fallback":"fallback val","title":"title val",'
                        '"fields":[{"title":"field title1",'
                        '"value":"field value1","short":"0"}]}]'),
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
        response_type='in_channel',
        replace_original=False,
        delete_original=True,
    )

    call = bot.call_queue.pop()
    assert call.method == 'chat.postMessage'
    assert call.data == {
        'channel': channel.id,
        'text': text,
        'parse': parse,
        'link_names': bool2str(True),
        'attachments': ('[{"fallback":"fallback val","title":"title val",'
                        '"fields":[{"title":"field title1",'
                        '"value":"field value1","short":"0"}]}]'),
        'unfurl_links': bool2str(False),
        'unfurl_media': bool2str(True),
        'username': username,
        'as_user': bool2str(False),
        'icon_url': icon_url,
        'icon_emoji': icon_emoji,
        'thread_ts': thread_ts,
        'reply_broadcast': bool2str(True),
        'response_type': 'in_channel',
        'replace_original': bool2str(False),
        'delete_original': bool2str(True),
    }
