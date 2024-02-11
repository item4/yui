from datetime import timedelta

import pytest
from time_machine import travel

from yui.apps.date.weekend import auto_weekend_loading
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


@pytest.mark.asyncio()
@travel(datetime(2018, 10, 8, 0), tick=False)
async def test_weekend_start(bot_config):
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
async def test_weekend_half(bot_config):
    bot_config.CHANNELS["general"] = "C1"
    bot_config.WEEKEND_LOADING_TIME = [0, 12]
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")

    await auto_weekend_loading(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "주말로딩… [■■■■■■■■■■□□□□□□□□□□] 50.00%"
