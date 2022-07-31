import asyncio
import os
from hashlib import md5
from urllib.parse import urlencode

import pytest

from tests.util import FakeBot

from yui.apps.weather.weather import WeatherResponseError
from yui.apps.weather.weather import clothes_by_temperature
from yui.apps.weather.weather import degree_to_direction
from yui.apps.weather.weather import get_geometric_info_by_address
from yui.apps.weather.weather import get_weather_by_coordinate
from yui.apps.weather.weather import weather
from yui.utils import json


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
async def test_get_weather_wrong_geometric_info(response_mock):
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
async def test_get_weather_with_wrong_openweather_coordination(response_mock):
    response_mock.get(
        "https://api.openweathermap.org/data/2.5/weather?"
        "lat=123&lon=456&appid=asdf&units=metric",
        body=json.dumps({}),
        status=404,
        headers={"Content-Type": "application/json"},
    )

    with pytest.raises(WeatherResponseError):
        await get_weather_by_coordinate(123, 456, "asdf")


def test_degree_to_direction():
    cases = [
        (0, "N"),
        (22.5, "NNE"),
        (45, "NE"),
        (67.5, "ENE"),
        (90, "E"),
        (112.5, "ESE"),
        (135, "SE"),
        (157.5, "SSE"),
        (180, "S"),
        (202.5, "SSW"),
        (225, "SW"),
        (247.5, "WSW"),
        (270, "W"),
        (292.5, "WNW"),
        (315, "NW"),
        (337.5, "NNW"),
    ]

    for degree, direction in cases:
        assert direction == degree_to_direction(degree)


@pytest.mark.asyncio
async def test_weather(bot_config, cache, openweather_api_key, google_api_key):
    bot_config.OPENWEATHER_API_KEY = openweather_api_key
    bot_config.GOOGLE_API_KEY = google_api_key

    bot = FakeBot(bot_config, cache=cache)
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")

    event = bot.create_message("C1", "U1", "1234.5678")

    async with bot.begin():
        await weather(bot, event, addr1)

    said = bot.call_queue.pop(0)

    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["thread_ts"] == "1234.5678"
    assert said.data["text"] != "해당 주소는 찾을 수 없어요!"
    assert said.data["text"] != "날씨 API 접근 중 에러가 발생했어요!"
    assert said.data["text"] != "검색 결과가 없어요! OpenWeather로 검색할 수 없는 곳 같아요!"


unavailable_address = "테스트 장소"


@pytest.mark.asyncio
async def test_weather_geocoding_error(bot_config, cache, response_mock):
    response_mock.get(
        "https://maps.googleapis.com/maps/api/geocode/json?"
        + urlencode(
            {"region": "kr", "address": unavailable_address, "key": "qwer"}
        ),
        body=json.dumps({"results": [], "status": "ZERO_RESULTS"}),
        headers={"Content-Type": "application/json"},
    )

    bot_config.OPENWEATHER_API_KEY = "asdf"
    bot_config.GOOGLE_API_KEY = "qwer"

    bot = FakeBot(bot_config, cache=cache)
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")

    event = bot.create_message("C1", "U1", "1234.5678")

    async with bot.begin():
        await weather(bot, event, unavailable_address)

    said = bot.call_queue.pop(0)

    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "해당 주소는 찾을 수 없어요!"


@pytest.mark.asyncio
async def test_weather_openweather_error(bot_config, cache, response_mock):
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
        "https://api.openweathermap.org/data/2.5/weather?"
        "appid=asdf&lat=37.5034138&lon=126.7660309&units=metric",
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
        await weather(bot, event, addr1)

    said = bot.call_queue.pop(0)

    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "날씨 API 접근 중 에러가 발생했어요!"
