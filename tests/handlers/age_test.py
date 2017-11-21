import datetime

import pytest

from yui.event import create_event
from yui.handlers.age import age

from ..util import FakeBot


@pytest.mark.asyncio
async def test_age_command():
    bot = FakeBot()
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })
    kirito_birthday = datetime.date(2008, 10, 7)
    leeseha_birthday = datetime.date(2003, 6, 3)

    await age(bot, event, datetime.date(2000, 1, 1), kirito_birthday)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '기준일 기준으로 아직 태어나지 않았어요!'

    await age(bot, event, datetime.date(2000, 1, 1), leeseha_birthday)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '기준일 기준으로 아직 태어나지 않았어요!'

    await age(bot, event, datetime.date(2008, 10, 7), kirito_birthday)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '2008년 10월 07일 출생자는 2008년 10월 07일 기준으로 1세 (만 0세)에요! '
        '출생일로부터 0일 지났어요. 다음 생일까지 365일 남았어요.'
    )

    await age(bot, event, datetime.date(2003, 6, 3), leeseha_birthday)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '2003년 06월 03일 출생자는 2003년 06월 03일 기준으로 1세 (만 0세)에요! '
        '출생일로부터 0일 지났어요. 다음 생일까지 366일 남았어요.'
    )

    await age(bot, event, datetime.date(2009, 1, 1), kirito_birthday)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '2008년 10월 07일 출생자는 2009년 01월 01일 기준으로 2세 (만 0세)에요! '
        '출생일로부터 86일 지났어요. 다음 생일까지 279일 남았어요.'
    )

    await age(bot, event, datetime.date(2004, 1, 1), leeseha_birthday)
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '2003년 06월 03일 출생자는 2004년 01월 01일 기준으로 2세 (만 0세)에요! '
        '출생일로부터 212일 지났어요. 다음 생일까지 154일 남았어요.'
    )
