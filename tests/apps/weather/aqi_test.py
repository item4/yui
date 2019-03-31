import os
import re
from urllib.parse import urlencode

import pytest

import ujson

from yui.apps.weather.aqi import (
    AQIRecord,
    aqi,
    get_aqi,
    get_aqi_description,
    get_geometric_info_by_address,
)

from ...util import FakeBot

result_pattern_re = re.compile(
    r'.+? 기준으로 가장 근접한 관측소의\d{4}년 \d{2}월 \d{2}일 \d{2}시 계측 자료에요.\n\n'
    r'\* 종합 AQI: \d+(?:\.\d+)? - (?:좋음|보통|민감군 영향|나쁨|매우 나쁨|위험)\(.+?\)\n'
    r'\* PM2\.5: \d+(?:\.\d+)? \(최소 \d+(?:\.\d+)? / 최대 \d+(?:\.\d+)?\)\n'
    r'\* PM10: \d+(?:\.\d+)? \(최소 \d+(?:\.\d+)? / 최대 \d+(?:\.\d+)?\)\n'
    r'\* 오존: \d+(?:\.\d+)? \(최소 \d+(?:\.\d+)? / 최대 \d+(?:\.\d+)?\)\n'
    r'\* 이산화 질소: \d+(?:\.\d+)? \(최소 \d+(?:\.\d+)? / 최대 \d+(?:\.\d+)?\)\n'
    r'\* 이산화 황: \d+(?:\.\d+)? \(최소 \d+(?:\.\d+)? / 최대 \d+(?:\.\d+)?\)\n'
    r'\* 일산화 탄소: \d+(?:\.\d+)? \(최소 \d+(?:\.\d+)? / 최대 \d+(?:\.\d+)?\)'
)


@pytest.fixture()
def fx_aqi_api_token():
    token = os.getenv('AQI_API_TOKEN')
    if not token:
        pytest.skip('Can not test this without AQI_API_TOKEN envvar')
    return token


@pytest.fixture()
def fx_google_api_key():
    key = os.getenv('GOOGLE_API_KEY')
    if not key:
        pytest.skip('Can not test this without GOOGLE_API_KEY envvar')
    return key


@pytest.mark.asyncio
async def test_get_geometric_info_by_address(fx_google_api_key):
    full_address, lat, lng = await get_geometric_info_by_address(
        '부천',
        fx_google_api_key,
    )

    assert full_address == '대한민국 경기도 부천시'
    assert lat == 37.5034138
    assert lng == 126.7660309

    full_address, lat, lng = await get_geometric_info_by_address(
        '서울',
        fx_google_api_key,
    )

    assert full_address == '대한민국 서울특별시 서울특별시'
    assert lat == 37.566535
    assert lng == 126.9779692

    with pytest.raises(IndexError):
        await get_geometric_info_by_address(
            '🙄  🐰😴😰🏄😋😍🍦😮🐖😫🍭🚬🚪🐳😞😎🚠😖🍲🙉😢🚔🐩👪🐮🚍🐎👱🎿😸👩🚇🍟👧🎺😒',
            fx_google_api_key,
        )


@pytest.mark.asyncio
async def test_get_aqi(fx_aqi_api_token):
    result = await get_aqi(37.5034138, 126.9779692, fx_aqi_api_token)

    if result is None:
        pytest.skip('AQI Server problem')
    assert isinstance(result, AQIRecord)


@pytest.mark.asyncio
async def test_get_aqi_wrong_idx(response_mock):
    response_mock.get(
        'https://api.waqi.info/feed/geo:123;456/?token=asdf',
        body=ujson.dumps({'data': {'idx': 'wrong'}}),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get(
        'https://api.waqi.info/api/feed/@wrong/obs.en.json',
        body=ujson.dumps({'rxs': {'obs': [{'status': '404'}]}}),
        headers={'Content-Type': 'application/json'},
    )

    result = await get_aqi(123, 456, 'asdf')

    assert result is None


def test_get_aqi_description():
    assert get_aqi_description(0).startswith('좋음')
    assert get_aqi_description(50).startswith('좋음')
    assert get_aqi_description(51).startswith('보통')
    assert get_aqi_description(100).startswith('보통')
    assert get_aqi_description(101).startswith('민감군 영향')
    assert get_aqi_description(150).startswith('민감군 영향')
    assert get_aqi_description(151).startswith('나쁨')
    assert get_aqi_description(200).startswith('나쁨')
    assert get_aqi_description(201).startswith('매우 나쁨')
    assert get_aqi_description(300).startswith('매우 나쁨')
    assert get_aqi_description(301).startswith('위험')
    assert get_aqi_description(400).startswith('위험')


@pytest.mark.asyncio
async def test_aqi(fx_config, fx_aqi_api_token, fx_google_api_key):
    fx_config.AQI_API_TOKEN = fx_aqi_api_token
    fx_config.GOOGLE_API_KEY = fx_google_api_key

    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')

    event = bot.create_message('C1', 'U1', '1234.5678')

    await aqi(bot, event, '부천')

    said = bot.call_queue.pop(0)

    if said.data['text'] == '현재 AQI 서버의 상태가 좋지 않아요! 나중에 다시 시도해주세요!':
        pytest.skip('AQI Server problem')
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert result_pattern_re.match(said.data['text'])
    assert said.data['thread_ts'] == '1234.5678'

    await aqi(
        bot,
        event,
        '🙄  🐰😴😰🏄😋😍🍦😮🐖😫🍭🚬🚪🐳😞😎🚠😖🍲🙉😢🚔🐩👪🐮🚍🐎👱🎿😸👩🚇🍟👧🎺😒',
    )

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '해당 주소는 찾을 수 없어요!'


@pytest.mark.asyncio
async def test_aqi_error1(fx_config, response_mock):
    response_mock.get(
        'https://maps.googleapis.com/maps/api/geocode/json?' + urlencode({
            'address': '부천',
            'key': 'qwer',
        }),
        body=ujson.dumps({
            'results': [
                {
                    'address_components': [
                        {
                            'long_name': '부천',
                        },
                    ],
                    'geometry': {
                        'location': {
                            'lat': 37.5034138,
                            'lng': 126.7660309,
                        },
                    },
                },
            ],
        }),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get(
        'https://api.waqi.info/feed/geo:37.5034138;126.7660309/?token=asdf',
        body='null',
        headers={'Content-Type': 'application/json'},
    )

    fx_config.AQI_API_TOKEN = 'asdf'
    fx_config.GOOGLE_API_KEY = 'qwer'

    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')

    event = bot.create_message('C1', 'U1', '1234.5678')

    await aqi(bot, event, '부천')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '현재 AQI 서버의 상태가 좋지 않아요! 나중에 다시 시도해주세요!'
    )


@pytest.mark.asyncio
async def test_aqi_error2(fx_config, response_mock):
    response_mock.get(
        'https://maps.googleapis.com/maps/api/geocode/json?' + urlencode({
            'address': '부천',
            'key': 'qwer',
        }),
        body=ujson.dumps({
            'results': [
                {
                    'address_components': [
                        {
                            'long_name': '부천',
                        },
                    ],
                    'geometry': {
                        'location': {
                            'lat': 37.5034138,
                            'lng': 126.7660309,
                        },
                    },
                },
            ],
        }),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get(
        'https://api.waqi.info/feed/geo:37.5034138;126.7660309/?token=asdf',
        body=ujson.dumps({'data': {'idx': '5511'}}),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get(
        'https://api.waqi.info/api/feed/@5511/obs.en.json',
        body=ujson.dumps({'rxs': {'obs': [{'status': '404'}]}}),
        headers={'Content-Type': 'application/json'},
    )

    fx_config.AQI_API_TOKEN = 'asdf'
    fx_config.GOOGLE_API_KEY = 'qwer'

    bot = FakeBot(fx_config)
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'item4')

    event = bot.create_message('C1', 'U1', '1234.5678')

    await aqi(bot, event, '부천')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '현재 AQI 서버의 상태가 좋지 않아요! 나중에 다시 시도해주세요!'
    )
