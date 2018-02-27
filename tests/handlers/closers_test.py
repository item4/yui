import decimal

import pytest

from yui.event import create_event
from yui.handlers.closers import black_market_charge

from ..util import FakeBot


@pytest.mark.asyncio
async def test_age_command():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await black_market_charge(bot, event, decimal.Decimal(0))
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':closers: 0 크레딧 상품의 수수료는 3.00%인 0 크레딧 입니다.'
        ' 순 이익은 0 크레딧 입니다.'
    )

    await black_market_charge(bot, event, decimal.Decimal(500_000))
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':closers: 500,000 크레딧 상품의 수수료는 3.00%인 15,000 크레딧 입니다.'
        ' 순 이익은 485,000 크레딧 입니다.'
    )

    await black_market_charge(bot, event, decimal.Decimal(10_000_000))
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':closers: 10,000,000 크레딧 상품의 수수료는 3.50%인 350,000 크레딧 입니다.'
        ' 순 이익은 9,650,000 크레딧 입니다.'
    )

    await black_market_charge(bot, event, decimal.Decimal(20_000_000))
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':closers: 20,000,000 크레딧 상품의 수수료는 4.00%인 800,000 크레딧 입니다.'
        ' 순 이익은 19,200,000 크레딧 입니다.'
    )

    await black_market_charge(bot, event, decimal.Decimal(30_000_000))
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':closers: 30,000,000 크레딧 상품의 수수료는 4.50%인 1,350,000 크레딧 입니다.'
        ' 순 이익은 28,650,000 크레딧 입니다.'
    )

    await black_market_charge(bot, event, decimal.Decimal(140_000_000))
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':closers: 140,000,000 크레딧 상품의 수수료는 10.00%인'
        ' 14,000,000 크레딧 입니다. 순 이익은 126,000,000 크레딧 입니다.'
    )

    await black_market_charge(bot, event, decimal.Decimal(150_000_000))
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':closers: 150,000,000 크레딧 상품의 수수료는 10.00%인'
        ' 15,000,000 크레딧 입니다. 순 이익은 135,000,000 크레딧 입니다.'
    )

    await black_market_charge(bot, event, decimal.Decimal(500_000_000))
    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        ':closers: 500,000,000 크레딧 상품의 수수료는 10.00%인'
        ' 50,000,000 크레딧 입니다. 순 이익은 450,000,000 크레딧 입니다.'
    )
