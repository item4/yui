import pytest

from yui.event import create_event
from yui.handlers.hi import hi

from ..util import FakeBot


@pytest.mark.asyncio
async def test_hi_handler():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'kirito')
    event = create_event({
        'type': 'message',
        'channel': 'C1',
        'user': 'U1',
        'text': '안녕 유이',
    })

    await hi(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '안녕하세요! @kirito'

    event = create_event({
        'type': 'message',
        'channel': 'C1',
        'user': 'U1',
        'text': '안녕',
    })

    await hi(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '안녕하세요! @kirito'

    event = create_event({
        'type': 'message',
        'channel': 'C1',
        'user': 'U1',
        'text': '유이 안녕',
    })

    await hi(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '안녕하세요! @kirito'

    event = create_event({
        'type': 'message',
        'channel': 'C1',
        'user': 'U1',
        'text': '아무말 대잔치',
    })

    await hi(bot, event)

    assert not bot.call_queue
