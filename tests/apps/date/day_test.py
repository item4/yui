from datetime import timedelta

import pytest
from time_machine import travel

from yui.apps.date.day import holiday
from yui.apps.date.day import holiday_message
from yui.utils.datetime import datetime

from ...util import FakeBot


def test_holiday_message_spec():
    assert holiday_message.has_valid_spec()


@pytest.mark.parametrize(
    ("delta", "result"),
    [
        (timedelta(days=0), True),
        (timedelta(days=0, minutes=5), False),
        (timedelta(days=1), False),
        (timedelta(days=2), True),
        (timedelta(days=3), True),
        (timedelta(days=4), True),
        (timedelta(days=5), True),
        (timedelta(days=6), True),
    ],
)
def test_holiday_message_match(sunday, delta, result):
    assert holiday_message.match(sunday + delta) is result


@pytest.mark.asyncio
@travel(datetime(2019, 2, 6), tick=False)
async def test_holiday_task_at_holiday(bot_config, channel_id):
    bot_config.CHANNELS["general"] = channel_id
    bot = FakeBot(bot_config)
    await holiday_message(bot)
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == channel_id
    assert said.data["text"] == "오늘은 설날연휴! 행복한 휴일 되세요!"


@pytest.mark.asyncio
@travel(datetime(2019, 2, 7), tick=False)
async def test_holiday_task_at_workday(bot_config, channel_id):
    bot_config.CHANNELS["general"] = channel_id
    bot = FakeBot(bot_config)
    await holiday_message(bot)
    assert not bot.call_queue


@pytest.mark.asyncio
@travel(datetime(2019, 2, 4), tick=False)
async def test_holiday_command(bot_config):
    bot = FakeBot(bot_config)
    event = bot.create_message()

    # empty body
    await holiday(bot, event, "")
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "2019년 02월 04일: 설날연휴"

    # buggy input
    await holiday(bot, event, "버그발생")
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "인식할 수 없는 날짜 표현식이에요!"

    # full date
    await holiday(bot, event, "2019년 2월 4일")
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "2019년 02월 04일: 설날연휴"

    # no event
    await holiday(bot, event, "2019년 1월 4일")
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "2019년 01월 04일: 평일"

    # API error
    await holiday(bot, event, "2010년 1월 1일")
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "API가 해당 년월일시의 자료를 제공하지 않아요!"
