import pytest

from yui.apps.ping import ping

from ..util import FakeBot


@pytest.mark.asyncio
async def test_ping_command():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')
    event = bot.create_message('C1', 'U1')

    await ping(bot, event)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '@item4, pong!'
