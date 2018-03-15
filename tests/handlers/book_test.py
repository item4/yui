import os
import re

from attrdict import AttrDict

import pytest

from yui.event import create_event
from yui.handlers.book import book

from ..util import FakeBot

result_pattern_re = re.compile(
    r'키워드 \*(.+?)\* \(으\)로 네이버 책 DB 검색 결과,'
    r' 총 \d+(?:,\d{3})*개의 결과가 나왔어요\.'
    r' 그 중 상위 (\d+)개를 보여드릴게요!'
)


@pytest.fixture()
def fx_naver_client_id():
    token = os.getenv('NAVER_CLIENT_ID')
    if not token:
        pytest.skip('Can not test this without NAVER_CLIENT_ID envvar')
    return token


@pytest.fixture()
def fx_naver_client_secret():
    key = os.getenv('NAVER_CLIENT_SECRET')
    if not key:
        pytest.skip('Can not test this without NAVER_CLIENT_SECRET envvar')
    return key


@pytest.mark.asyncio
async def test_book(fx_naver_client_id, fx_naver_client_secret):
    config = AttrDict({
        'NAVER_CLIENT_ID': fx_naver_client_id,
        'NAVER_CLIENT_SECRET': fx_naver_client_secret,
    })
    bot = FakeBot(config)
    bot.add_channel('C1', 'general')

    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await book(bot, event, '소드 아트 온라인')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    match = result_pattern_re.match(said.data['text'])
    assert match
    assert match.group(1) == '소드 아트 온라인'
    assert match.group(2) == '3'

    await book(
        bot,
        event,
        '🙄  🐰😴😰🏄😋😍🍦😮🐖😫🍭🚬🚪🐳😞😎🚠😖🍲🙉😢🚔🐩👪🐮🚍🐎👱🎿😸👩🚇🍟👧🎺😒',
    )

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
