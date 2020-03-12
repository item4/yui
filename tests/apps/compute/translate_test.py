import os

import pytest

from yui.apps.compute.translate import _translate, detect_language, translate

from ...util import FakeBot


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


@pytest.fixture()
def bot(fx_config, fx_naver_client_id, fx_naver_client_secret):
    fx_config.NAVER_CLIENT_ID = fx_naver_client_id
    fx_config.NAVER_CLIENT_SECRET = fx_naver_client_secret
    return FakeBot(fx_config)


@pytest.fixture()
def header(fx_naver_client_id, fx_naver_client_secret):
    return {
        'X-Naver-Client-Id': fx_naver_client_id,
        'X-Naver-Client-Secret': fx_naver_client_secret,
    }


@pytest.mark.asyncio
async def test_detect_language(header):
    assert await detect_language(header, '안녕하세요. 제 이름은 유이에요.') == 'ko'
    assert await detect_language(header, 'こんにちは。私の名前はユです。') == 'ja'
    assert await detect_language(header, 'Hi. My name is Yui.') == 'en'


@pytest.mark.asyncio
async def test_private_translate_function(header):
    text = '안녕하세요. 제 이름은 YUI에요.'
    result = 'こんにちは。私の名前はYUIです。'
    assert await _translate(header, 'ko', 'ja', text) == result


@pytest.mark.asyncio
async def test_translate_command(bot):
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')

    event = bot.create_message('C1', 'U1')

    await translate(bot, event, None, 'ja', '안녕하세요. 제 이름은 YUI에요.' * 100)
    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '500자 이상의 긴 문장의 번역은 다른 번역기를 사용해주세요!'

    await translate(bot, event, 'php', 'ja', '안녕하세요. 제 이름은 YUI에요.')
    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '원문 언어가 올바르지 않아요!'

    await translate(bot, event, None, 'ja', '?' * 100)
    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '원문 언어를 추론하는데에 실패했어요!'

    await translate(bot, event, 'ko', 'php', '안녕하세요. 제 이름은 YUI에요.')
    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '결과값 언어가 올바르지 않아요!'

    await translate(bot, event, 'en', 'en', '안녕하세요. 제 이름은 YUI에요.')
    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '원문 언어와 결과값 언어가 같아요!'

    await translate(bot, event, 'id', 'th', 'orange')
    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '인도네시아어에서 태국어로의 번역은 현재 지원되지 않아요!'

    await translate(bot, event, None, 'ja', '안녕하세요. 제 이름은 YUI에요.')
    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '한국어 원문: 안녕하세요. 제 이름은 YUI에요.\n' '일본어 번역: こんにちは。私の名前はYUIです。'
    )

    await translate(bot, event, 'ko', 'ko', '안녕하세요. 제 이름은 YUI에요.')
    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '한국어 원문: 안녕하세요. 제 이름은 YUI에요.\n' '영어 번역: Hello. My name is YUI.'
    )
