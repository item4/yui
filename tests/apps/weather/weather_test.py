import asyncio
import os
import re
from hashlib import md5
from urllib.parse import urlencode

import pytest

from tests.util import FakeBot

from yui.apps.weather.weather import WeatherResponseError
from yui.apps.weather.weather import clothes_by_temperature
from yui.apps.weather.weather import degree_to_direction
from yui.apps.weather.weather import get_air_pollution_by_coordinate
from yui.apps.weather.weather import get_aqi_description
from yui.apps.weather.weather import get_geometric_info_by_address
from yui.apps.weather.weather import get_weather_by_coordinate
from yui.apps.weather.weather import weather
from yui.utils import json

# AQI 이외의 데이터는 모두 Optiona한 데이터이므로 정규식 매치에서 제외함.
result_pattern_re = re.compile(
    r".+? 기준으로 가장 근접한 관측소의 최근 자료에요.\n\n"
    r"\* 종합 AQI: (?:좋음|보통|민감군 영향|나쁨|매우 나쁨)\(.+?\)"
)


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


@pytest.mark.asyncio
async def test_get_air_pollution_with_wrong_coordination(response_mock):
    response_mock.get(
        "https://api.openweathermap.org/data/2.5/air_pollution?"
        "lat=123&lon=456&appid=asdf",
        body=json.dumps({}),
        status=404,
        headers={"Content-Type": "application/json"},
    )

    with pytest.raises(WeatherResponseError):
        await get_air_pollution_by_coordinate(123, 456, "asdf")


@pytest.mark.parametrize(
    "level, expected",
    [
        (1, "좋음"),
        (2, "보통"),
        (3, "민감군 영향"),
        (4, "나쁨"),
        (5, "매우 나쁨"),  # API Spec은 5단계가 최대입니다.
    ],
)
def test_get_aqi_description(level, expected):
    assert get_aqi_description(level).startswith(expected)


@pytest.mark.parametrize(
    "degree, direction",
    [
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
    ],
)
def test_degree_to_direction(degree, direction):
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

    weather_said = bot.call_queue.pop(0)

    assert weather_said.method == "chat.postMessage"
    assert weather_said.data["channel"] == "C1"
    assert weather_said.data["thread_ts"] == "1234.5678"
    assert weather_said.data["username"].endswith("날씨")

    assert weather_said.data["text"] != "해당 주소는 찾을 수 없어요!"
    assert weather_said.data["text"] != "날씨 API 접근 중 에러가 발생했어요!"
    assert (
        weather_said.data["text"] != "검색 결과가 없어요! OpenWeather로 검색할 수 없는 곳 같아요!"
    )

    air_pollution_said = bot.call_queue.pop(0)

    assert air_pollution_said.method == "chat.postMessage"
    assert air_pollution_said.data["channel"] == "C1"
    assert result_pattern_re.match(air_pollution_said.data["text"]) is not None
    assert air_pollution_said.data["username"].endswith("대기질")


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
    response_mock.get(
        "https://api.openweathermap.org/data/2.5/air_pollution?"
        "lat=37.5034138&lon=126.7660309&appid=asdf",
        body=json.dumps({}),
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
