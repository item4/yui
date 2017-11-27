import pytest

from yui.event import create_event
from yui.handlers.ping import ping

from ..util import FakeBot


@pytest.mark.asyncio
async def test_ping_command():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })
    user = {
        'user': {
            'name': 'item4',
        },
    }

    await ping(bot, event, user)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '@item4, pong!'
