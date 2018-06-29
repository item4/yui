import pytest

import ujson

from yui.event import create_event
from yui.handlers.joke import hassan, luwak, relax

from ..util import FakeBot


@pytest.mark.asyncio
async def test_hassan_handler():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'hunj')
    event = create_event({
        'type': 'message',
        'channel': 'C1',
        'user': 'U1',
        'text': '똑바로 서라 유이',
    })

    assert not await hassan(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '저한테 왜 그러세요 @hunj님?'

    event = create_event({
        'type': 'message',
        'channel': 'C1',
        'user': 'U1',
        'text': '아무말 대잔치',
    })

    assert await hassan(bot, event)

    assert not bot.call_queue


@pytest.mark.asyncio
async def test_relax_command():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await relax(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '유이에게 나쁜 것을 주입하려는 사악한 재벌은 이 너굴맨이 처리했으니 안심하라구!'
    )
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '너굴맨'


@pytest.mark.asyncio
async def test_luwak_command():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await luwak(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert len(ujson.loads(said.data['attachments']))
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '지옥에서 온 램지'
