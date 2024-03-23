from datetime import timedelta

import pytest
from time_machine import travel

from yui.apps.date.weekend import auto_weekend_loading
from yui.apps.date.weekend import auto_weekend_start
from yui.apps.date.weekend import weekend_loading
from yui.utils.datetime import datetime

from ...util import FakeBot


def test_auto_weekend_loading_spec():
    assert auto_weekend_loading.has_valid_spec()


@pytest.mark.parametrize(
    ("delta", "result"),
    [
        (timedelta(days=0), False),
        (timedelta(days=1), True),
        (timedelta(days=1, minutes=11), False),
        (timedelta(days=2), True),
        (timedelta(days=3), True),
        (timedelta(days=4), True),
        (timedelta(days=5), True),
        (timedelta(days=6), False),
    ],
)
def test_auto_weekend_loading_match(sunday, delta, result):
    assert auto_weekend_loading.match(sunday + delta) is result


def test_auto_weekend_start_spec():
    assert auto_weekend_start.has_valid_spec()


@pytest.mark.parametrize(
    ("delta", "result"),
    [
        (timedelta(days=0), False),
        (timedelta(days=1), False),
        (timedelta(days=2), False),
        (timedelta(days=3), False),
        (timedelta(days=4), False),
        (timedelta(days=5), False),
        (timedelta(days=6), True),
        (timedelta(days=6, minutes=11), False),
    ],
)
def test_auto_weekend_start_match(sunday, delta, result):
    assert auto_weekend_start.match(sunday + delta) is result


@pytest.mark.asyncio()
async def test_auto_weekend_start(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")

    await auto_weekend_start(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "주말이에요! 즐거운 주말 되세요!"


@pytest.mark.asyncio()
@travel(datetime(2018, 10, 8, 0), tick=False)
async def test_auto_weekend_loading_start(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot_config.WEEKEND_LOADING_TIME = [0, 12]
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")

    await auto_weekend_loading(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "주말로딩… [□□□□□□□□□□□□□□□□□□□□] 0.00%"


@pytest.mark.asyncio()
@travel(datetime(2018, 10, 10, 12), tick=False)
async def test_auto_weekend_loading_half(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot_config.WEEKEND_LOADING_TIME = [0, 12]
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")

    await auto_weekend_loading(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "주말로딩… [■■■■■■■■■■□□□□□□□□□□] 50.00%"


@pytest.mark.asyncio()
@travel(datetime(2018, 10, 8, 0), tick=False)
async def test_weekend_loading_start(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot_config.WEEKEND_LOADING_TIME = [0, 12]
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")
    event = bot.create_message("C1", "U1")

    await weekend_loading(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "주말로딩… [□□□□□□□□□□□□□□□□□□□□] 0.00%"


@pytest.mark.asyncio()
@travel(datetime(2018, 10, 10, 12), tick=False)
async def test_weekend_loading_half(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot_config.WEEKEND_LOADING_TIME = [0, 12]
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")
    event = bot.create_message("C1", "U1")

    await weekend_loading(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "주말로딩… [■■■■■■■■■■□□□□□□□□□□] 50.00%"


@pytest.mark.asyncio()
@travel(datetime(2018, 10, 13), tick=False)
async def test_weekend_loading_end(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot_config.WEEKEND_LOADING_TIME = [0, 12]
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")
    event = bot.create_message("C1", "U1")

    await weekend_loading(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "주말이에요! 즐거운 주말 되세요!"


@pytest.mark.asyncio()
@travel(datetime(2018, 10, 14), tick=False)
async def test_weekend_loading_over(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot_config.WEEKEND_LOADING_TIME = [0, 12]
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")
    event = bot.create_message("C1", "U1")

    await weekend_loading(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "주말이에요! 즐거운 주말 되세요!"
