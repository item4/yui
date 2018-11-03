import pytest

from yui.api.encoder import bool2str
from yui.types.channel import PrivateChannel

from ..util import FakeBot


@pytest.mark.asyncio
async def test_slack_api_groups_info():
    group_id = 'G1'
    group = PrivateChannel(id='G2', name='secret', creator='U0', last_read=0)

    bot = FakeBot()

    await bot.api.groups.info(group_id)
    call = bot.call_queue.pop()
    assert call.method == 'groups.info'
    assert call.data == {
        'channel': 'G1',
        'include_locale': bool2str(False),
    }

    await bot.api.groups.info(group)
    call = bot.call_queue.pop()
    assert call.method == 'groups.info'
    assert call.data == {
        'channel': 'G2',
        'include_locale': bool2str(False),
    }


@pytest.mark.asyncio
async def test_slack_api_groups_list():
    bot = FakeBot()

    await bot.api.groups.list()
    call = bot.call_queue.pop()
    assert call.method == 'groups.list'
    assert call.data == {
        'exclude_archived': bool2str(True),
        'exclude_members': bool2str(True),
    }
