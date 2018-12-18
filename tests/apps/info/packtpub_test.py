import re

import pytest

from yui.api import Attachment
from yui.apps.info.packtpub import (
    PACKTPUB_URL,
    auto_packtpub_dotd,
    packtpub_dotd,
    parse_packtpub_dotd,
)
from yui.session import client_session

from ...util import FakeBot

book_result_pattern_re = re.compile(
    r'키워드 \*(.+?)\* \(으\)로 네이버 책 DB 검색 결과,'
    r' 총 \d+(?:,\d{3})*개의 결과가 나왔어요\.'
    r' 그 중 상위 (\d+)개를 보여드릴게요!'
)


async def fetch_obj_or_skip_test_if_no_dotd():
    async with client_session() as session:
        async with session.get(PACKTPUB_URL) as resp:
            html = await resp.text()

    result = parse_packtpub_dotd(html)

    if result is None:
        pytest.skip('dotd error')

    return result


@pytest.mark.asyncio
async def test_parse_packtpub_dotd():
    result = await fetch_obj_or_skip_test_if_no_dotd()

    assert isinstance(result, Attachment)
    assert result.fallback.endswith(PACKTPUB_URL)
    assert result.title
    assert result.title_link == PACKTPUB_URL
    assert result.text == (
        f'오늘의 Packt Book Deal of The Day: {result.title} - {PACKTPUB_URL}'
    )
    assert result.image_url.startswith('https://')


@pytest.mark.asyncio
async def test_no_parse_packtpub_dotd():
    html = '<!doctype html>\n<html></html>'

    result = parse_packtpub_dotd(html)

    assert result is None

    html = '<!doctype html>\n<html><div class="dotd-title"></div></html>'

    result = parse_packtpub_dotd(html)

    assert result is None


@pytest.mark.asyncio
async def test_packtpub_dotd():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')

    event = bot.create_message('C1', 'U1')

    await fetch_obj_or_skip_test_if_no_dotd()
    await packtpub_dotd(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '오늘자 PACKT Book의 무료책이에요!'
    assert said.data['attachments']


@pytest.mark.asyncio
async def test_no_packtpub_dotd(response_mock):
    response_mock.get(PACKTPUB_URL, body='<!doctype html>\n<html></html>')

    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')

    event = bot.create_message('C1', 'U1')

    await packtpub_dotd(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '오늘은 PACKT Book의 무료책이 없는 것 같아요'


@pytest.mark.asyncio
async def test_auto_packtpub_dotd(fx_config):
    assert auto_packtpub_dotd.cron.spec == '5 11 * * *'

    fx_config.CHANNELS = {
        'general': 'general',
    }
    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')

    await fetch_obj_or_skip_test_if_no_dotd()
    await auto_packtpub_dotd(bot)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '오늘자 PACKT Book의 무료책이에요!'
    assert said.data['attachments']
