import re

from aiohttp import client_exceptions

import pytest

import ujson

from yui.apps.weather.aws import API_URL, aws, clothes_by_temperature

from ...util import FakeBot

COOLTIME = re.compile(r'아직 쿨타임이에요! \d+시 \d+분 이후로 다시 시도해주세요!')


def test_clothes_by_temperature():
    cases = [
        clothes_by_temperature(5),
        clothes_by_temperature(9),
        clothes_by_temperature(11),
        clothes_by_temperature(16),
        clothes_by_temperature(19),
        clothes_by_temperature(22),
        clothes_by_temperature(26),
        clothes_by_temperature(30),
    ]
    assert len(cases) == len(set(cases))


@pytest.mark.asyncio
async def test_aws(response_mock):
    response_mock.get(  # 1
        API_URL,
        exception=client_exceptions.ClientPayloadError(),
    )
    response_mock.get(  # 2
        API_URL,
        body=ujson.dumps({
            'observed_at': '2019-12-31T00:00:00+0900',
            'records': [
                {
                    'id': 433,
                    'name': '부천',
                    'height': 29,
                    'rain': {
                        'is_raining': 'Clear',
                        'rain15': 0.0,
                        'rain60': 0.0,
                        'rain3h': 0.0,
                        'rain6h': 0.0,
                        'rain12h': 0.0,
                        'rainday': 0.0,
                    },
                    'temperature': -9.0,
                    'wind1': {
                        'direction_code': 320.5,
                        'direction_text': 'NW',
                        'velocity': 1.5,
                    },
                    'wind10': {
                        'direction_code': 298.0,
                        'direction_text': 'WNW',
                        'velocity': 1.3,
                    },
                    'humidity': None,
                    'atmospheric': None,
                    'address': '경기도 부천시 중동',
                },
            ]
        }),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get(  # 3
        API_URL,
        body=ujson.dumps({
            'observed_at': '2019-12-31T00:00:00+0900',
            'records': [
                {
                    'id': 433,
                    'name': '부천',
                    'height': 29,
                    'rain': {
                        'is_raining': 'Clear',
                        'rain15': 0.0,
                        'rain60': 0.0,
                        'rain3h': 0.0,
                        'rain6h': 0.0,
                        'rain12h': 0.0,
                        'rainday': 0.0,
                    },
                    'temperature': -9.0,
                    'wind1': {
                        'direction_code': 320.5,
                        'direction_text': 'NW',
                        'velocity': 1.5,
                    },
                    'wind10': {
                        'direction_code': 298.0,
                        'direction_text': 'WNW',
                        'velocity': 1.3,
                    },
                    'humidity': None,
                    'atmospheric': None,
                    'address': '경기도 부천시 중동',
                },
                {
                    'id': 429,
                    'name': '부천원미',
                    'height': 16,
                    'rain': {
                        'is_raining': 'Unknown',
                        'rain15': None,
                        'rain60': None,
                        'rain3h': None,
                        'rain6h': None,
                        'rain12h': None,
                        'rainday': None,
                    },
                    'temperature': None,
                    'wind1': {
                        'direction_code': None,
                        'direction_text': 'Unavailable',
                        'velocity': None,
                    },
                    'wind10': {
                        'direction_code': None,
                        'direction_text': 'Unavailable',
                        'velocity': None,
                    },
                    'humidity': None,
                    'atmospheric': None,
                    'address': '경기도 부천시 중동',
                },
            ]
        }),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get(  # 4
        API_URL,
        body=ujson.dumps({
            'observed_at': '2019-12-31T13:00:00+0900',
            'records': [
                {
                    'id': 433,
                    'name': '가상',
                    'height': 100,
                    'rain': {
                        'is_raining': 'Rain',
                        'rain15': 10.0,
                        'rain60': 20.0,
                        'rain3h': 40.0,
                        'rain6h': 80.0,
                        'rain12h': 160.0,
                        'rainday': 320.0,
                    },
                    'temperature': 15.0,
                    'wind1': {
                        'direction_code': 320.5,
                        'direction_text': 'NW',
                        'velocity': 1.5,
                    },
                    'wind10': {
                        'direction_code': 298.0,
                        'direction_text': 'WNW',
                        'velocity': 1.3,
                    },
                    'humidity': 43,
                    'atmospheric': 1035.1,
                    'address': '가상시 가상구',
                },
            ]
        }),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get(  # 5
        API_URL,
        body=ujson.dumps({
            'observed_at': '2019-12-31T13:00:00+0900',
            'records': [
                {
                    'id': 433,
                    'name': '가상',
                    'height': 100,
                    'rain': {
                        'is_raining': 'Rain',
                        'rain15': 10.0,
                        'rain60': 20.0,
                        'rain3h': 40.0,
                        'rain6h': 80.0,
                        'rain12h': 160.0,
                        'rainday': 320.0,
                    },
                    'temperature': -15.0,
                    'wind1': {
                        'direction_code': 320.5,
                        'direction_text': 'NW',
                        'velocity': 1.5,
                    },
                    'wind10': {
                        'direction_code': 298.0,
                        'direction_text': 'WNW',
                        'velocity': 1.3,
                    },
                    'humidity': 43,
                    'atmospheric': 1035.1,
                    'address': '가상시 가상구',
                },
            ]
        }),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get(  # 6
        API_URL,
        body=ujson.dumps({
            'observed_at': '2019-12-31T13:00:00+0900',
            'records': [
                {
                    'id': 433,
                    'name': '가상',
                    'height': 100,
                    'rain': {
                        'is_raining': 'Clear',
                        'rain15': 0.0,
                        'rain60': 0.0,
                        'rain3h': 0.0,
                        'rain6h': 0.0,
                        'rain12h': 0.0,
                        'rainday': 0.0,
                    },
                    'temperature': -15.0,
                    'wind1': {
                        'direction_code': 320.5,
                        'direction_text': 'NW',
                        'velocity': 1.5,
                    },
                    'wind10': {
                        'direction_code': 298.0,
                        'direction_text': 'WNW',
                        'velocity': 1.3,
                    },
                    'humidity': 43,
                    'atmospheric': 1035.1,
                    'address': '가상시 가상구',
                },
            ]
        }),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get(  # 7
        API_URL,
        body=ujson.dumps({
            'observed_at': '2019-12-31T13:00:00+0900',
            'records': [
                {
                    'id': 433,
                    'name': f'가상{i}',
                    'height': 100,
                    'rain': {
                        'is_raining': 'Clear',
                        'rain15': 0.0,
                        'rain60': 0.0,
                        'rain3h': 0.0,
                        'rain6h': 0.0,
                        'rain12h': 0.0,
                        'rainday': 0.0,
                    },
                    'temperature': -15.0,
                    'wind1': {
                        'direction_code': 320.5,
                        'direction_text': 'NW',
                        'velocity': 1.5,
                    },
                    'wind10': {
                        'direction_code': 298.0,
                        'direction_text': 'WNW',
                        'velocity': 1.3,
                    },
                    'humidity': 43,
                    'atmospheric': 1035.1,
                    'address': '가상시 가상구',
                } for i in range(10)
            ]
        }),
        headers={'Content-Type': 'application/json'},
    )
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')

    event = bot.create_message('C1', 'U1', ts='1234.56')

    # too short keyword
    await aws(bot, event, False, '1')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '검색어가 너무 짧아요! 2글자 이상의 검색어를 사용해주세요!'
    )
    assert 'thread_ts' not in said.data

    # 1 API error
    await aws(bot, event, False, '부천')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '날씨 API 접근 중 에러가 발생했어요!'
    assert 'thread_ts' not in said.data

    # 2 match first mode
    await aws(bot, event, False, '부천')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '[2019년 12월 31일 00시 00분@부천/경기도 부천시 중동]'
        ' 강수: 아니오 / -9℃ / 바람: 북서 1.5㎧'
        '\n\n추천 의상: 패딩, 두꺼운 코트, 목도리, 기모제품'
    )
    assert said.data['username'] == '부천 날씨'
    assert said.data['icon_emoji'] == ':crescent_moon:'
    assert 'thread_ts' not in said.data

    # 3 fuzzy togather mode
    await aws(bot, event, True, '부천')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '[2019년 12월 31일 00시 00분@부천/경기도 부천시 중동]'
        ' 강수: 아니오 / -9℃ / 바람: 북서 1.5㎧'
        '\n\n추천 의상: 패딩, 두꺼운 코트, 목도리, 기모제품'
    )
    assert said.data['username'] == '부천 날씨'
    assert said.data['icon_emoji'] == ':crescent_moon:'
    assert said.data['thread_ts'] == event.ts

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '[2019년 12월 31일 00시 00분@부천원미/경기도 부천시 중동]'
        ' 강수: 모름'
    )
    assert said.data['username'] == '부천원미 날씨'
    assert said.data['icon_emoji'] == ':crescent_moon:'
    assert said.data['thread_ts'] == event.ts

    # 4 test rain
    await aws(bot, event, False, '가상')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '[2019년 12월 31일 13시 00분@가상/가상시 가상구]'
        ' 강수: 예(15min: 10/일일: 320) / 15℃ / 바람: 북서 1.5㎧'
        ' / 습도: 43% / 해면기압: 1035.1hPa'
        '\n\n추천 의상: 얇은 재킷, 가디건, 간절기 야상, 맨투맨, 니트, 살구색 스타킹'
    )
    assert said.data['username'] == '가상 날씨'
    assert said.data['icon_emoji'] == ':umbrella_with_rain_drops:'
    assert 'thread_ts' not in said.data

    # 5 test snow
    await aws(bot, event, False, '가상')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '[2019년 12월 31일 13시 00분@가상/가상시 가상구]'
        ' 강수: 예(15min: 10/일일: 320) / -15℃ / 바람: 북서 1.5㎧'
        ' / 습도: 43% / 해면기압: 1035.1hPa'
        '\n\n추천 의상: 패딩, 두꺼운 코트, 목도리, 기모제품'
    )
    assert said.data['username'] == '가상 날씨'
    assert said.data['icon_emoji'] == ':snowflake:'
    assert 'thread_ts' not in said.data

    # 6 test sunny
    await aws(bot, event, False, '가상')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '[2019년 12월 31일 13시 00분@가상/가상시 가상구]'
        ' 강수: 아니오 / -15℃ / 바람: 북서 1.5㎧'
        ' / 습도: 43% / 해면기압: 1035.1hPa'
        '\n\n추천 의상: 패딩, 두꺼운 코트, 목도리, 기모제품'
    )
    assert said.data['username'] == '가상 날씨'
    assert said.data['icon_emoji'] == ':sunny:'
    assert 'thread_ts' not in said.data

    # 7 hit cooltime
    await aws(bot, event, True, '가상')

    assert len(bot.call_queue) == 10
    for i in range(10):
        said = bot.call_queue.pop(0)
        assert said.method == 'chat.postMessage'
        assert said.data['channel'] == 'C1'
        assert said.data['text'] == (
            f'[2019년 12월 31일 13시 00분@가상{i}/가상시 가상구]'
            ' 강수: 아니오 / -15℃ / 바람: 북서 1.5㎧'
            ' / 습도: 43% / 해면기압: 1035.1hPa'
            '\n\n추천 의상: 패딩, 두꺼운 코트, 목도리, 기모제품'
        )
        assert said.data['username'] == f'가상{i} 날씨'
        assert said.data['icon_emoji'] == ':sunny:'
        assert said.data['thread_ts'] == event.ts

    assert aws.last_call['C1']

    # block by cooltime
    await aws(bot, event, False, '가상')

    assert len(bot.call_queue) == 1

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert COOLTIME.match(said.data['text'])

    assert 'thread_ts' not in said.data
