import pytest

from yui.api.encoder import bool2str
from yui.types.channel import PublicChannel

from ..util import FakeBot


@pytest.mark.asyncio
async def test_slack_api_channels_history():
    channel_id = 'C1234'
    channel = PublicChannel(id='C4567', name='test', creator='U0', last_read=0)

    bot = FakeBot()

    await bot.api.channels.history(
        channel_id,
        count=1234,
        inclusive=True,
        latest='123',
        oldest='456',
        unreads=False,
    )
    call = bot.call_queue.pop()
    assert call.method == 'channels.history'
    assert call.data == {
        'channel': channel_id,
        'count': '1234',
        'inclusive': bool2str(True),
        'latest': '123',
        'oldest': '456',
        'unreads': bool2str(False),
    }
    await bot.api.channels.history(
        channel,
        count=1234,
        inclusive=True,
        latest='123',
        oldest='456',
        unreads=False,
    )
    call = bot.call_queue.pop()
    assert call.method == 'channels.history'
    assert call.data == {
        'channel': channel.id,
        'count': '1234',
        'inclusive': bool2str(True),
        'latest': '123',
        'oldest': '456',
        'unreads': bool2str(False),
    }


@pytest.mark.asyncio
async def test_slack_api_channels_info():
    channel_id = 'C1234'
    channel = PublicChannel(id='C4567', name='test', creator='U0', last_read=0)

    bot = FakeBot()

    await bot.api.channels.info(channel_id)
    call = bot.call_queue.pop()
    assert call.method == 'channels.info'
    assert call.data == {
        'channel': channel_id,
        'include_locale': bool2str(False),
    }

    await bot.api.channels.info(channel)
    call = bot.call_queue.pop()
    assert call.method == 'channels.info'
    assert call.data == {
        'channel': channel.id,
        'include_locale': bool2str(False),
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
        'exclude_archived': bool2str(exclude_archived),
        'exclude_members': bool2str(exclude_members),
        'limit': '12',
    }
