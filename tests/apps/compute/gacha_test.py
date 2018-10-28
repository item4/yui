from decimal import Decimal

import pytest

from yui.apps.compute.gacha import Gacha, to_percent
from yui.event import Message, create_event

from ...util import FakeBot


def test_class():
    g = Gacha()
    assert g.name == '가챠'
    assert g.route_list


def test_get_short_help():
    g = Gacha()
    assert g.get_short_help('.')


def test_get_full_help():
    g = Gacha()
    assert g.get_full_help('.')


@pytest.mark.asyncio
async def test_fallback(fx_config):
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')
    g = Gacha()

    event: Message = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await g.fallback(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == f'Usage: `{bot.config.PREFIX}help 가챠`'


@pytest.mark.asyncio
async def test_collect(fx_config):
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')
    g = Gacha()

    event: Message = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await g.collect(g, bot, event, 30)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '상품 1개 구입시 30종류의 특전 중 하나를 무작위로 100% 확률로 준다고 가정할 때 '
        '30종류의 특전을 모두 모으려면, 평균적으로 120(`119.85`)개의 상품을 구입해야 '
        '전체 수집에 성공할 수 있어요!'
    )


@pytest.mark.asyncio
async def test_challenge(fx_config):
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')
    g = Gacha()

    event: Message = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await g.challenge(g, bot, event, -1, '0.05')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '성공횟수는 1회 이상, 10,000회 이하로 입력해주세요!'

    await g.challenge(g, bot, event, 9999999, '0.05')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '성공횟수는 1회 이상, 10,000회 이하로 입력해주세요!'

    await g.challenge(g, bot, event, 1, '아무말 대잔치')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '정상적인 확률을 입력해주세요!'

    await g.challenge(g, bot, event, 1, '0.000000001')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '확률값은 0.001% 이상, 99% 이하로 입력해주세요!'

    await g.challenge(g, bot, event, 1, '999999')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '확률값은 0.001% 이상, 99% 이하로 입력해주세요!'

    await g.challenge(g, bot, event, 1000, '0.00001')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '입력하신 확률값에 비해 성공 횟수가 너무 많아요!'

    await g.challenge(g, bot, event, 1, '0.05')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '5% 확률의 도전을 1번 성공시키려면 몇 회의 도전이 필요한지 알려드릴게요!\n'
        '- 1번 시도하시면 5% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 6번 시도하시면 26.49% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 14번 시도하시면 51.23% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 28번 시도하시면 76.21% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 59번 시도하시면 95.15% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 90번 시도하시면 99.01% 확률로 목표 횟수만큼 성공할 수 있어요!'
    )

    await g.challenge(g, bot, event, 1, '3%')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '3% 확률의 도전을 1번 성공시키려면 몇 회의 도전이 필요한지 알려드릴게요!\n'
        '- 1번 시도하시면 3% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 10번 시도하시면 26.25% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 23번 시도하시면 50.36% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 46번 시도하시면 75.36% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 99번 시도하시면 95.09% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 152번 시도하시면 99.02% 확률로 목표 횟수만큼 성공할 수 있어요!'
    )

    await g.challenge(g, bot, event, 1, '95%')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '95% 확률의 도전을 1번 성공시키려면 몇 회의 도전이 필요한지 알려드릴게요!\n'
        '- 1번 시도하시면 95% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 2번 시도하시면 99.74% 확률로 목표 횟수만큼 성공할 수 있어요!'
    )

    await g.challenge(g, bot, event, 1, '98.00000000%')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '98% 확률의 도전을 1번 성공시키려면 몇 회의 도전이 필요한지 알려드릴게요!\n'
        '- 1번 시도하시면 98% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 2번 시도하시면 99.96% 확률로 목표 횟수만큼 성공할 수 있어요!'
    )

    await g.challenge(g, bot, event, 10, '0.1%')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '0.1% 확률의 도전을 10번 성공시키려면 몇 회의 도전이 필요한지 알려드릴게요!\n'
        '- 2,964번 시도하시면 0.1% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 7,727번 시도하시면 25% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 9,669번 시도하시면 50% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 11,913번 시도하시면 75% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 15,702번 시도하시면 95% 확률로 목표 횟수만큼 성공할 수 있어요!\n'
        '- 18,779번 시도하시면 99% 확률로 목표 횟수만큼 성공할 수 있어요!'
    )


def test_to_percent():
    assert to_percent(Decimal('12.300040000')) == '1230.004'
    assert to_percent(Decimal('12.300000000')) == '1230'
    assert to_percent(Decimal('12'), Decimal('1')) == '1200'
