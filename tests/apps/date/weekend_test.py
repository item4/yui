from freezegun import freeze_time

import pytest

from yui.apps.date.weekend import auto_weekend_loading
from yui.utils.datetime import datetime

from ...util import FakeBot


@pytest.mark.asyncio
@freeze_time(datetime(2018, 10, 8, 0))
async def test_weekend_start(fx_config):
    fx_config.CHANNELS['general'] = 'general'
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')

    await auto_weekend_loading(bot)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == ('주말로딩… [□□□□□□□□□□□□□□□□□□□□] 0.00%')


@pytest.mark.asyncio
@freeze_time(datetime(2018, 10, 10, 12))
async def test_weekend_half(fx_config):
    fx_config.CHANNELS['general'] = 'general'
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')

    await auto_weekend_loading(bot)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == ('주말로딩… [■■■■■■■■■■□□□□□□□□□□] 50.00%')
