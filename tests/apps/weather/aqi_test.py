import asyncio
import os
import re
from hashlib import md5
from urllib.parse import urlencode

import pytest

from yui.apps.weather.aqi import AirPollutionResponseError
from yui.apps.weather.aqi import aqi
from yui.apps.weather.aqi import get_air_pollution_by_coordinate
from yui.apps.weather.aqi import get_aqi_description
from yui.apps.weather.aqi import get_geometric_info_by_address
from yui.utils import json

from ...util import FakeBot

result_pattern_re = re.compile(
    r".+? 기준으로 가장 근접한 관측소의 최근 자료에요.\n\n"
    r"\* 종합 AQI: (?:좋음|보통|민감군 영향|나쁨|매우 나쁨)\(.+?\)\n"
    r"\* PM2\.5: \d+(?:\.\d+)?μg/m3\n"
    r"\* PM10: \d+(?:\.\d+)?μg/m3\n"
    r"\* 오존: \d+(?:\.\d+)?μg/m3\n"
    r"\* 일산화 질소: \d+(?:\.\d+)?μg/m3\n"
    r"\* 이산화 질소: \d+(?:\.\d+)?μg/m3\n"
    r"\* 이산화 황: \d+(?:\.\d+)?μg/m3\n"
    r"\* 일산화 탄소: \d+(?:\.\d+)?μg/m3\n"
    r"\* 암모니아: \d+(?:\.\d+)?μg/m3"
)

addr1 = "부천"
addr1_md5 = md5(addr1.encode()).hexdigest()
addr2 = "서울"
addr2_md5 = md5(addr2.encode()).hexdigest()


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def openweather_api_key():
    token = os.getenv("OPENWEATHER_API_KEY")
    if not token:
        pytest.skip("Can not test this without OPENWEATHER_API_KEY envvar")
    return token


@pytest.fixture()
def google_api_key():
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        pytest.skip("Can not test this without GOOGLE_API_KEY envvar")
    return key


@pytest.mark.asyncio
async def test_get_geometric_info_by_address(google_api_key):
    full_address, lat, lng = await get_geometric_info_by_address(
        addr1,
        google_api_key,
    )

    assert full_address == "대한민국 경기도 부천시"
    assert lat == 37.5034138
    assert lng == 126.7660309

    full_address, lat, lng = await get_geometric_info_by_address(
        addr2,
        google_api_key,
    )

    assert full_address == "대한민국 서울특별시"
    assert lat == 37.566535
    assert lng == 126.9779692


@pytest.mark.asyncio
async def test_get_aqi_wrong_geometric_info(response_mock):
    addr = "WRONG"
    key = "XXX"
    response_mock.get(
        "https://maps.googleapis.com/maps/api/geocode/json"
        f"?region=kr&address={addr}&key=XXX",
        body=json.dumps(
            {
                "results": [],
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    with pytest.raises(IndexError):
        await get_geometric_info_by_address(
            addr,
            key,
        )


@pytest.mark.asyncio
async def test_get_air_pollution_with_wrong_coordination(response_mock):
    response_mock.get(
        "https://api.openweathermap.org/data/2.5/air_pollution?"
        "lat=123&lon=456&appid=asdf",
        body=json.dumps({}),
        status=404,
        headers={"Content-Type": "application/json"},
    )

    with pytest.raises(AirPollutionResponseError):
        await get_air_pollution_by_coordinate(123, 456, "asdf")


def test_get_aqi_description():
    assert get_aqi_description(0).startswith("좋음")
    assert get_aqi_description(1).startswith("좋음")
    assert get_aqi_description(2).startswith("보통")
    assert get_aqi_description(3).startswith("민감군 영향")
    assert get_aqi_description(4).startswith("나쁨")
    assert get_aqi_description(5).startswith("매우 나쁨")
    # API Spec은 5단계가 최대입니다.
    assert get_aqi_description(6).startswith("매우 나쁨")


@pytest.mark.asyncio
async def test_aqi(bot_config, cache, openweather_api_key, google_api_key):
    bot_config.OPENWEATHER_API_KEY = openweather_api_key
    bot_config.GOOGLE_API_KEY = google_api_key

    bot = FakeBot(bot_config, cache=cache)
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")

    event = bot.create_message("C1", "U1", "1234.5678")

    async with bot.begin():
        await aqi(bot, event, addr1)

    said = bot.call_queue.pop(0)

    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["thread_ts"] == "1234.5678"
    assert said.data["text"] != "해당 주소는 찾을 수 없어요!"
    assert said.data["text"] != "날씨 API 접근 중 에러가 발생했어요!"
    assert said.data["text"] != "검색 결과가 없어요! OpenWeather로 검색할 수 없는 곳 같아요!"


unavailable_address = "테스트 장소"


@pytest.mark.asyncio
async def test_aqi_geocoding_error(bot_config, cache, response_mock):
    response_mock.get(
        "https://maps.googleapis.com/maps/api/geocode/json?"
        + urlencode(
            {"region": "kr", "address": unavailable_address, "key": "ghjk"}
        ),
        body=json.dumps({"results": [], "status": "ZERO_RESULTS"}),
        headers={"Content-Type": "application/json"},
    )

    bot_config.OPENWEATHER_API_KEY = "asdf"
    bot_config.GOOGLE_API_KEY = "ghjk"

    bot = FakeBot(bot_config, cache=cache)
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")

    event = bot.create_message("C1", "U1", "1234.5678")

    async with bot.begin():
        await aqi(bot, event, unavailable_address)

    said = bot.call_queue.pop(0)

    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "해당 주소는 찾을 수 없어요!"


@pytest.mark.asyncio
async def test_aqi_openweather_error(bot_config, cache, response_mock):
    response_mock.get(
        "https://maps.googleapis.com/maps/api/geocode/json?"
        + urlencode({"region": "kr", "address": addr1, "key": "qwer"}),
        body=json.dumps(
            {
                "results": [
                    {
                        "formatted_address": "대한민국 경기도 부천시",
                        "geometry": {
                            "location": {
                                "lat": 37.5034138,
                                "lng": 126.7660309,
                            },
                        },
                    },
                ],
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    response_mock.get(
        "https://api.openweathermap.org/data/2.5/air_pollution?"
        "appid=asdf&lat=37.5034138&lon=126.7660309",
        body="null",
        status=401,
        headers={"Content-Type": "application/json"},
    )

    bot_config.OPENWEATHER_API_KEY = "asdf"
    bot_config.GOOGLE_API_KEY = "qwer"

    bot = FakeBot(bot_config, cache=cache)
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")

    event = bot.create_message("C1", "U1", "1234.5678")

    async with bot.begin():
        await aqi(bot, event, addr1)

    said = bot.call_queue.pop(0)

    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "날씨 API 접근 중 에러가 발생했어요!"
