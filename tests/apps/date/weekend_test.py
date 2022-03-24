import pytest

from time_machine import travel

from yui.apps.date.weekend import auto_weekend_loading
from yui.utils.datetime import datetime

from ...util import FakeBot


@pytest.mark.asyncio
@travel(datetime(2018, 10, 8, 0), tick=False)
async def test_weekend_start(bot_config):
    bot_config.CHANNELS['general'] = 'C1'
    bot_config.WEEKEND_LOADING_TIME = [0, 12]
    bot = FakeBot(bot_config)
    bot.add_channel('C1', 'general')

    await auto_weekend_loading(bot)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '주말로딩… [□□□□□□□□□□□□□□□□□□□□] 0.00%'


@pytest.mark.asyncio
@travel(datetime(2018, 10, 10, 12), tick=False)
async def test_weekend_half(bot_config):
    bot_config.CHANNELS['general'] = 'C1'
    bot_config.WEEKEND_LOADING_TIME = [0, 12]
    bot = FakeBot(bot_config)
    bot.add_channel('C1', 'general')

    await auto_weekend_loading(bot)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '주말로딩… [■■■■■■■■■■□□□□□□□□□□] 50.00%'
