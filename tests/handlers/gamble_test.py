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

    assert not await dice(bot, event, 0, 0)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '정상적인 범위를 입력해주세요!'

    assert not await dice(bot, event, 0, 100, seed=100)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '딜러'
    assert said.data['text'] == (
        '유이가 기도하며 주사위를 굴려줬습니다. 18입니다.'
    )

    assert not await dice(bot, event, 0, 100, seed=104)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '딜러'
    assert said.data['text'] == '콩'

    assert not await dice(bot, event, 0, 100, seed=166)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '딜러'
    assert said.data['text'] == '콩콩'
