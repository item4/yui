import os
import re

import pytest

import ujson

from yui.apps.search.book import book
from yui.event import create_event

from ...util import FakeBot

book_result_pattern_re = re.compile(
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
async def test_book(fx_config, fx_naver_client_id, fx_naver_client_secret):
    fx_config.NAVER_CLIENT_ID = fx_naver_client_id
    fx_config.NAVER_CLIENT_SECRET = fx_naver_client_secret
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')

    event = create_event({
        'type': 'message',
        'channel': 'C1',
        'ts': '1234.5678',
    })

    await book(bot, event, '소드 아트 온라인')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    match = book_result_pattern_re.match(said.data['text'])
    assert match
    assert match.group(1) == '소드 아트 온라인'
    assert len(ujson.loads(said.data['attachments'])) == int(match.group(2))
    assert said.data['thread_ts'] == '1234.5678'

    await book(
        bot,
        event,
        '🙄  🐰😴😰🏄😋😍🍦😮🐖😫🍭🚬🚪🐳😞😎🚠😖🍲🙉😢🚔🐩👪🐮🚍🐎👱🎿😸👩🚇🍟👧🎺😒',
    )

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '검색 결과가 없어요!'
