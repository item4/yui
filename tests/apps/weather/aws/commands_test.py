import copy

import pytest

from yui.apps.shared.cache import JSONCache
from yui.apps.weather.aws.commands import aws
from yui.utils.datetime import now

from ....util import FakeBot


@pytest.mark.asyncio
async def test_aws(fx_sess):
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')

    event = bot.create_message('C1', 'U1', ts='1234.56')

    await aws(bot, event, fx_sess, False, False, '서울')

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
                "name": "가나",
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
                "address": "지구 반대편 가나",
            },
        ]
    }
    cache.created_at = now()

    with fx_sess.begin():
        fx_sess.add(cache)

    # not found
    await aws(bot, event, fx_sess, False, False, '부천')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '검색결과가 없어요!'
    assert 'thread_ts' not in said.data

    # rain
    await aws(bot, event, fx_sess, False, False, '서울')

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

    # snow
    await aws(bot, event, fx_sess, False, False, '강남')

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
    assert 'thread_ts' not in said.data

    # sun
    await aws(bot, event, fx_sess, False, False, '가나')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '[2018년 12월 30일 13시 16분@가나/지구 반대편 가나]'
        ' 강수: 아니오'
        ' / 12.34℃ / 바람: 남남서 11.11㎧ / 습도: 55% / 해면기압: 2345.67hPa'
    )
    assert said.data['username'] == '가나 날씨'
    assert said.data['icon_emoji'] == ':sunny:'
    assert 'thread_ts' not in said.data

    # moon
    new_body = copy.deepcopy(cache.body)
    new_body['observed_at'] = '2018-12-30T22:16:00+0900'
    cache.body = new_body
    with fx_sess.begin():
        fx_sess.add(cache)

    await aws(bot, event, fx_sess, False, False, '가나')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '[2018년 12월 30일 22시 16분@가나/지구 반대편 가나]'
        ' 강수: 아니오'
        ' / 12.34℃ / 바람: 남남서 11.11㎧ / 습도: 55% / 해면기압: 2345.67hPa'
    )
    assert said.data['username'] == '가나 날씨'
    assert said.data['icon_emoji'] == ':crescent_moon:'
    assert 'thread_ts' not in said.data

    # include address
    await aws(bot, event, fx_sess, False, True, '서울')

    assert len(bot.call_queue) == 2

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '서울 날씨'
    assert said.data['thread_ts'] == event.ts

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '강남 날씨'
    assert said.data['thread_ts'] == event.ts

    await aws(bot, event, fx_sess, False, True, '가나')

    assert len(bot.call_queue) == 1

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '가나 날씨'
    assert 'thread_ts' not in said.data

    # fuzzy
    await aws(bot, event, fx_sess, True, False, '강남')

    assert len(bot.call_queue) == 2

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '강남 날씨'
    assert said.data['thread_ts'] == event.ts

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '가나 날씨'
    assert said.data['thread_ts'] == event.ts

    await aws(bot, event, fx_sess, True, False, '서울')

    assert len(bot.call_queue) == 1

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '서울 날씨'
    assert 'thread_ts' not in said.data

    # fuzzy + include address
    await aws(bot, event, fx_sess, True, True, '서울')

    assert len(bot.call_queue) == 2

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '서울 날씨'
    assert said.data['thread_ts'] == event.ts

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '강남 날씨'
    assert said.data['thread_ts'] == event.ts

    await aws(bot, event, fx_sess, True, True, '가나')

    assert len(bot.call_queue) == 2

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '가나 날씨'
    assert said.data['thread_ts'] == event.ts

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['username'] == '강남 날씨'
    assert said.data['thread_ts'] == event.ts
