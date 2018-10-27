import pytest

from yui.apps.compute.gacha import Gacha
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
