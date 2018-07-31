import pytest

from yui.event import create_event
from yui.handlers.gamble import dice

from ..util import FakeBot


@pytest.mark.asyncio
async def test_dice_handler():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'user')
    event = create_event({
        'type': 'message',
        'channel': 'C1',
        'user': 'U1',
        'text': '주사위',
    })

    assert not await dice(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '딜러'
