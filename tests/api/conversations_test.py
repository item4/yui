import pytest

from yui.api.encoder import bool2str


@pytest.mark.asyncio
async def test_slack_api_conversations_history(bot):
    channel = bot.add_channel('C4567', 'test')
    channel_id = 'C1234'

    await bot.api.conversations.history(
        channel_id,
        cursor='asdf',
        inclusive=True,
        latest='123',
        limit=42,
        oldest='456',
    )
    call = bot.call_queue.pop()
    assert call.method == 'conversations.history'
    assert call.data == {
        'channel': channel_id,
        'cursor': 'asdf',
        'inclusive': bool2str(True),
        'latest': '123',
        'limit': '42',
        'oldest': '456',
    }
    await bot.api.conversations.history(
        channel,
        cursor='asdf',
        inclusive=True,
        latest='123',
        limit=42,
        oldest='456',
    )
    call = bot.call_queue.pop()
    assert call.method == 'conversations.history'
    assert call.data == {
        'channel': channel.id,
        'cursor': 'asdf',
        'inclusive': bool2str(True),
        'latest': '123',
        'limit': '42',
        'oldest': '456',
    }


@pytest.mark.asyncio
async def test_slack_api_conversations_replies(bot):
    channel = bot.add_channel('C4567', 'test')
    channel_id = 'C1234'
    ts = '123456.7'

    await bot.api.conversations.replies(
        channel_id,
        ts,
        cursor='asdf',
        inclusive=True,
        latest='123',
        limit=42,
        oldest='456',
    )
    call = bot.call_queue.pop()
    assert call.method == 'conversations.replies'
    assert call.data == {
        'channel': channel_id,
        'ts': ts,
        'cursor': 'asdf',
        'inclusive': bool2str(True),
        'latest': '123',
        'limit': '42',
        'oldest': '456',
    }
    await bot.api.conversations.replies(
        channel,
        ts,
        cursor='asdf',
        inclusive=True,
        latest='123',
        limit=42,
        oldest='456',
    )
    call = bot.call_queue.pop()
    assert call.method == 'conversations.replies'
    assert call.data == {
        'channel': channel.id,
        'ts': ts,
        'cursor': 'asdf',
        'inclusive': bool2str(True),
        'latest': '123',
        'limit': '42',
        'oldest': '456',
    }


@pytest.mark.asyncio
async def test_slack_api_conversations_info(bot):
    channel = bot.add_channel('C4567', 'test')
    channel_id = 'C1234'

    await bot.api.conversations.info(
        channel_id,
        include_locale=False,
        include_num_members=True,
    )
    call = bot.call_queue.pop()
    assert call.method == 'conversations.info'
    assert call.data == {
        'channel': channel_id,
        'include_locale': bool2str(False),
        'include_num_members': bool2str(True),
    }

    await bot.api.conversations.info(
        channel,
        include_locale=False,
        include_num_members=True,
    )
    call = bot.call_queue.pop()
    assert call.method == 'conversations.info'
    assert call.data == {
        'channel': channel.id,
        'include_locale': bool2str(False),
        'include_num_members': bool2str(True),
    }


@pytest.mark.asyncio
async def test_slack_api_conversations_list(bot):
    cursor = '1234asdf'
    exclude_archived = False
    limit = 12
    types = 'private_channel'
    team_id = 'T1'

    await bot.api.conversations.list(
        cursor=cursor,
        exclude_archived=exclude_archived,
        limit=limit,
        team_id=team_id,
        types=types,
    )
    call = bot.call_queue.pop()
    assert call.method == 'conversations.list'
    assert call.data == {
        'cursor': cursor,
        'exclude_archived': bool2str(exclude_archived),
        'limit': str(limit),
        'team_id': team_id,
        'types': types,
    }


@pytest.mark.asyncio
async def test_slack_api_conversations_open(bot):
    channel_id = 'C1234'
    channel = bot.add_channel(channel_id, 'test')
    user_id = 'U1234'
    user = bot.add_user(user_id, 'tester')
    user2_id = 'U5678'
    bot.add_user(user2_id, 'tester2')
    return_im = True

    with pytest.raises(ValueError):
        await bot.api.conversations.open(
            channel=channel_id,
            users=[user_id],
        )
    with pytest.raises(ValueError):
        await bot.api.conversations.open()

    await bot.api.conversations.open(
        channel=channel_id,
        return_im=return_im,
    )
    call = bot.call_queue.pop()
    assert call.method == 'conversations.open'
    assert call.data == {
        'channel': channel_id,
        'return_im': bool2str(return_im),
    }

    await bot.api.conversations.open(
        channel=channel,
    )
    call = bot.call_queue.pop()
    assert call.method == 'conversations.open'
    assert call.data == {
        'channel': channel_id,
    }

    await bot.api.conversations.open(
        users=[user, user2_id],
    )
    call = bot.call_queue.pop()
    assert call.method == 'conversations.open'
    assert 'users' in call.data
    assert set(call.data['users'].split(',')) == {user_id, user2_id}
