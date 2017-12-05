import pytest

from yui.api.encoder import bool2str
from yui.api.type import Attachment, Field

from ..util import FakeBot


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
    assert call.data == {
        'channel': channel,
        'text': text,
        'as_user': bool2str(True),
    }

    await bot.api.chat.postMessage(channel=channel, attachments=attachments)

    call = bot.call_queue.pop()
    assert call.method == 'chat.postMessage'
    assert call.data == {
        'channel': channel,
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
    )

    call = bot.call_queue.pop()
    assert call.method == 'chat.postMessage'
    assert call.data == {
        'channel': channel,
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
    }
