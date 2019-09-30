import copy
import re

import pytest

from yui.apps.shared.cache import JSONCache
from yui.apps.weather.aws.commands import aws
from yui.utils.datetime import now

from ....util import FakeBot

COOLTIME = re.compile(r'아직 쿨타임이에요! \d+시 \d+분 이후로 다시 시도해주세요!')


@pytest.mark.asyncio
async def test_aws(fx_sess):
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')

    event = bot.create_message('C1', 'U1', ts='1234.56')

    await aws(bot, event, fx_sess, '서울')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '날씨 정보 검색 준비가 진행중이에요. 잠시만 기다려주세요!'
    assert 'thread_ts' not in said.data

    cache = JSONCache()
    cache.name = 'aws'
    cache.body = {
        'observed_at': '2018-12-30T13:16:00+0900',
        'records': [
            {
                "id": 1,
                "name": "서울",
                "height": 1234,
                "rain": {
                    "is_raining": "Rain",
                    "rain15": 15.1,
                    "rain60": 60.2,
                    "rain3h": 180.3,
                    "rain6h": 360.4,
                    "rain12h": 720.5,
                    "rainday": 1440.6,
                },
                "temperature": 12.34,
                "wind1": {
                    "direction_code": 999.9,
                    "direction_text": "SSW",
                    "velocity": 11.11,
                },
                "wind10": {
                    "direction_code": 888.8,
                    "direction_text": "NNE",
                    "velocity": 22.22,
                },
                "humidity": 55,
                "atmospheric": 2345.67,
                "address": "서울특별시 가구",
            },
            {
                "id": 2,
                "name": "강남",
                "height": 1234,
                "rain": {
                    "is_raining": "Rain",
                    "rain15": 15.1,
                    "rain60": 60.2,
                    "rain3h": 180.3,
                    "rain6h": 360.4,
                    "rain12h": 720.5,
                    "rainday": 1440.6,
                },
                "temperature": -12.34,
                "wind1": {
                    "direction_code": 999.9,
                    "direction_text": "SSW",
                    "velocity": 11.11,
                },
                "wind10": {
                    "direction_code": 888.8,
                    "direction_text": "NNE",
                    "velocity": 22.22,
                },
                "humidity": 55,
                "atmospheric": 2345.67,
                "address": "서울특별시 강남구",
            },
            {
                "id": 2,
                "name": "강남2",
                "height": 1234,
                "rain": {
                    "is_raining": "Clear",
                    "rain15": 0,
                    "rain60": 0,
                    "rain3h": 0,
                    "rain6h": 0,
                    "rain12h": 0,
                    "rainday": 0,
                },
                "temperature": 12.34,
                "wind1": {
                    "direction_code": 999.9,
                    "direction_text": "SSW",
                    "velocity": 11.11,
                },
                "wind10": {
                    "direction_code": 888.8,
                    "direction_text": "NNE",
                    "velocity": 22.22,
                },
                "humidity": 55,
                "atmospheric": 2345.67,
                "address": "강남2",
            },
        ]
    }
    cache.created_at = now()

    with fx_sess.begin():
        fx_sess.add(cache)

    # short keyword
    await aws(bot, event, fx_sess, '1')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '검색어가 너무 짧아요! 2글자 이상의 검색어를 사용해주세요!'
    )
    assert 'thread_ts' not in said.data

    # not found
    await aws(bot, event, fx_sess, '부천')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '검색결과가 없어요! 한국 기상청 AWS가 설치되지 않은 장소 같아요!'
    )
    assert 'thread_ts' not in said.data

    # found 1
    await aws(bot, event, fx_sess, '서울')

    assert len(bot.call_queue) == 1

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '[2018년 12월 30일 13시 16분@서울/서울특별시 가구]'
        ' 강수: 예(15min: 15.1/일일: 1440.6)'
        ' / 12.34℃ / 바람: 남남서 11.11㎧ / 습도: 55% / 해면기압: 2345.67hPa'
    )
    assert said.data['username'] == '서울 날씨'
    assert said.data['icon_emoji'] == ':umbrella_with_rain_drops:'
    assert 'thread_ts' not in said.data

    # found 2+
    await aws(bot, event, fx_sess, '강남')

    assert len(bot.call_queue) == 2

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '[2018년 12월 30일 13시 16분@강남/서울특별시 강남구]'
        ' 강수: 예(15min: 15.1/일일: 1440.6)'
        ' / -12.34℃ / 바람: 남남서 11.11㎧ / 습도: 55% / 해면기압: 2345.67hPa'
    )
    assert said.data['username'] == '강남 날씨'
    assert said.data['icon_emoji'] == ':snowflake:'
    assert said.data['thread_ts'] == '1234.56'

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '[2018년 12월 30일 13시 16분@강남2/강남2]'
        ' 강수: 아니오'
        ' / 12.34℃ / 바람: 남남서 11.11㎧ / 습도: 55% / 해면기압: 2345.67hPa'
    )
    assert said.data['username'] == '강남2 날씨'
    assert said.data['icon_emoji'] == ':sunny:'
    assert said.data['thread_ts'] == '1234.56'

    # hit cooltime
    new_body = copy.deepcopy(cache.body)
    for _ in range(5):
        new_body['records'] += new_body['records']
    cache.body = new_body
    with fx_sess.begin():
        fx_sess.add(cache)

    await aws(bot, event, fx_sess, '강남')

    assert len(bot.call_queue) > 5
    bot.call_queue.clear()
    assert aws.last_call['C1']

    # block by cooltime
    await aws(bot, event, fx_sess, '강남')

    assert len(bot.call_queue) == 1

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert COOLTIME.match(said.data['text'])

    assert 'thread_ts' not in said.data
