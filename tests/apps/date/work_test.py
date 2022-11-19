import pytest
from time_machine import travel

from yui.apps.date.work import work_end
from yui.apps.date.work import work_start
from yui.utils.datetime import datetime

from ...util import FakeBot


@pytest.mark.asyncio
@travel(datetime(2018, 10, 8, 9), tick=False)
async def test_work_start_monday(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")

    await work_start(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["username"] == "현실부정중인 직장인"
    assert said.data["attachments"]


@pytest.mark.asyncio
@travel(datetime(2018, 10, 10, 9), tick=False)
async def test_work_start_normal(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")

    await work_start(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["username"] == "노동자 핫산"
    assert said.data["text"] == "한국인들은 세계 누구보다 출근을 사랑하면서 왜 본심을 숨기는 걸까?"


@pytest.mark.asyncio
@travel(datetime(2018, 10, 9, 9), tick=False)
async def test_work_start_holiday(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")

    await work_start(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["username"] == "너굴맨"
    assert said.data["text"] == "오늘은 한글날! 출근하라는 상사는 이 너굴맨이 처리했으니 안심하라구!"


@pytest.mark.asyncio
@travel(datetime(2018, 10, 8, 18), tick=False)
async def test_work_end_18_normal(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")

    await work_end(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["username"] == "칼퇴의 요정"
    assert said.data["text"] == "6시가 되었습니다. 9시에 출근하신 분들은 칼같이 퇴근하시길 바랍니다."


@pytest.mark.asyncio
@travel(datetime(2018, 10, 9, 18), tick=False)
async def test_work_end_18_holiday(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")

    await work_end(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["username"] == "집사가 집에 있어서 기분 좋은 고양이"
    assert said.data["text"] == "한글날 만세! 6시인데 집사 퇴근 안 기다려도 되니까 좋다냥!"


@pytest.mark.asyncio
@travel(datetime(2018, 10, 8, 19), tick=False)
async def test_work_end_19_normal(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")

    await work_end(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["username"] == "칼퇴의 요정"
    assert said.data["text"] == "7시가 되었습니다. 10시에 출근하신 분들은 칼같이 퇴근하시길 바랍니다."


@pytest.mark.asyncio
@travel(datetime(2018, 10, 9, 19), tick=False)
async def test_work_end_19_holiday(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")

    await work_end(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["username"] == "집사가 집에 있어서 기분 좋은 고양이"
    assert said.data["text"] == "한글날 만세! 7시인데 집사 퇴근 안 기다려도 되니까 좋다냥!"
