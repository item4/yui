import pytest

from yui.event import create_event
from yui.handlers.select import select

from ..util import FakeBot


@pytest.mark.asyncio
async def test_select_command():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })
    seed = 1

    await select(bot, event, ' ', 'cat dog', seed)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '선택결과: cat'

    await select(bot, event, '/', 'cat/dog', seed)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '선택결과: cat'

    await select(bot, event, ',', 'cat, dog', seed)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '선택결과: cat'
