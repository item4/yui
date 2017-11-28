import pytest

from yui.type import PrivateChannel

from ..util import FakeBot


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
