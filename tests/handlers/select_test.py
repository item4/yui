import pytest

from yui.event import create_event
from yui.handlers.select import select

from ..util import FakeBot


@pytest.mark.asyncio
async def test_select_command():
    bot = FakeBot()
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })
    seed = 1

    await select(bot, event, ' ', 'cat dog', seed)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == 'cat'

    await select(bot, event, '/', 'cat/dog', seed)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == 'cat'

    await select(bot, event, ',', 'cat, dog', seed)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == 'cat'
