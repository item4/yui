import re

import pytest

from yui.apps.weather.pongdang import pongdang

from ...util import FakeBot

RESPONSE_PATTERN = re.compile(
    r'\d{4}년 \d{2}월 \d{2}일 \d{2}시 \d{2}분' r' 기준 한강 수온은 \d+(?:\.\d+)?°C에요!'
)


@pytest.mark.asyncio
async def test_pongdang():
    bot = FakeBot()
    bot.add_channel('C1', 'test')
    bot.add_user('U1', 'tester')
    event = bot.create_message('C1', 'U1')

    await pongdang(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert RESPONSE_PATTERN.match(said.data['text'])
