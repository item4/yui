from freezegun import freeze_time

import pytest

from yui.apps.date.day import holiday
from yui.utils.datetime import datetime

from ...util import FakeBot


@pytest.mark.asyncio
@freeze_time(datetime(2019, 2, 4))
async def test_holiday_command(fx_config):
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')
    event = bot.create_message('C1', 'U1')

    # empty body
    await holiday(bot, event, '')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '2019년 02월 04일: 설날연휴'

    # buggy input
    await holiday(bot, event, '버그발생')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '인식할 수 없는 날짜 표현식이에요!'

    # full date
    await holiday(bot, event, '2019년 2월 4일')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '2019년 02월 04일: 설날연휴'

    # no event
    await holiday(bot, event, '2019년 1월 4일')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '2019년 01월 04일: 평일'

    # API error
    await holiday(bot, event, '2010년 1월 1일')
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == 'API가 해당 년월일시의 자료를 제공하지 않아요!'
