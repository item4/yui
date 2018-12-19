import os

from freezegun import freeze_time

import pytest

from yui.apps.date.work import work_end, work_start
from yui.utils.datetime import datetime

from ...util import FakeBot


@pytest.fixture()
def fx_tdcproject_key():
    key = os.getenv('TDCPROJECT_KEY')
    if not key:
        pytest.skip('Can not test this without TDCPROJECT_KEY envvar')
    return key


@pytest.mark.asyncio
@freeze_time(datetime(2018, 10, 8, 9))
async def test_work_start_monday(fx_config, fx_tdcproject_key):
    fx_config.TDCPROJECT_KEY = fx_tdcproject_key
    fx_config.CHANNELS['general'] = 'general'
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')

    await work_start(bot)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '현실부정중인 직장인'
    assert said.data['as_user'] == '0'
    assert said.data['attachments']


@pytest.mark.asyncio
@freeze_time(datetime(2018, 10, 10, 9))
async def test_work_start_normal(fx_config, fx_tdcproject_key):
    fx_config.TDCPROJECT_KEY = fx_tdcproject_key
    fx_config.CHANNELS['general'] = 'general'
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')

    await work_start(bot)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '노동자'
    assert said.data['as_user'] == '0'
    assert said.data['attachments']


@pytest.mark.asyncio
@freeze_time(datetime(2018, 10, 9, 9))
async def test_work_start_holiday(fx_config, fx_tdcproject_key):
    fx_config.TDCPROJECT_KEY = fx_tdcproject_key
    fx_config.CHANNELS['general'] = 'general'
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')

    await work_start(bot)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '너굴맨'
    assert said.data['as_user'] == '0'
    assert said.data['text'] == (
        '오늘은 한글날! 출근하라는 상사는 이 너굴맨이 처리했으니 안심하라구!'
    )


@pytest.mark.asyncio
@freeze_time(datetime(2018, 10, 8, 18))
async def test_work_end_18_normal(fx_config, fx_tdcproject_key):
    fx_config.TDCPROJECT_KEY = fx_tdcproject_key
    fx_config.CHANNELS['general'] = 'general'
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')

    await work_end(bot)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '칼퇴의 요정'
    assert said.data['as_user'] == '0'
    assert said.data['text'] == (
        '6시가 되었습니다. 9시에 출근하신 분들은 칼같이 퇴근하시길 바랍니다.'
    )


@pytest.mark.asyncio
@freeze_time(datetime(2018, 10, 9, 18))
async def test_work_end_18_holiday(fx_config, fx_tdcproject_key):
    fx_config.TDCPROJECT_KEY = fx_tdcproject_key
    fx_config.CHANNELS['general'] = 'general'
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')

    await work_end(bot)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '집사가 집에 있어서 기분 좋은 고양이'
    assert said.data['as_user'] == '0'
    assert said.data['text'] == (
        '한글날 만세! 6시인데 집사 퇴근 안 기다려도 되니까 좋다냥!'
    )


@pytest.mark.asyncio
@freeze_time(datetime(2018, 10, 8, 19))
async def test_work_end_19_normal(fx_config, fx_tdcproject_key):
    fx_config.TDCPROJECT_KEY = fx_tdcproject_key
    fx_config.CHANNELS['general'] = 'general'
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')

    await work_end(bot)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '칼퇴의 요정'
    assert said.data['as_user'] == '0'
    assert said.data['text'] == (
        '7시가 되었습니다. 10시에 출근하신 분들은 칼같이 퇴근하시길 바랍니다.'
    )


@pytest.mark.asyncio
@freeze_time(datetime(2018, 10, 9, 19))
async def test_work_end_19_holiday(fx_config, fx_tdcproject_key):
    fx_config.TDCPROJECT_KEY = fx_tdcproject_key
    fx_config.CHANNELS['general'] = 'general'
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')

    await work_end(bot)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '집사가 집에 있어서 기분 좋은 고양이'
    assert said.data['as_user'] == '0'
    assert said.data['text'] == (
        '한글날 만세! 7시인데 집사 퇴근 안 기다려도 되니까 좋다냥!'
    )
