import re

import pytest
from yarl import URL

from tests.util import FakeBot

from yui.apps.weather.commands import weather

# AQI 이외의 데이터는 모두 Optional한 데이터이므로 정규식 매치에서 제외함.
result_pattern_re = re.compile(
    r".+? 기준으로 가장 근접한 관측소의 최근 자료에요.\n\n"
    r"\* 종합 AQI: (?:좋음|보통|민감군 영향|나쁨|매우 나쁨)\(.+?\)"
)


@pytest.mark.asyncio
async def test_weather(
    bot_config, cache, openweather_api_key, google_api_key, address
):
    bot_config.OPENWEATHER_API_KEY = openweather_api_key
    bot_config.GOOGLE_API_KEY = google_api_key

    bot = FakeBot(bot_config, cache=cache)
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")

    event = bot.create_message("C1", "U1", "1234.5678")

    async with bot.begin():
        await weather(bot, event, address)

    weather_said = bot.call_queue.pop(0)

    assert weather_said.method == "chat.postMessage"
    assert weather_said.data["channel"] == "C1"

    if weather_said.data["text"] == "날씨 API 접근 중 에러가 발생했어요!":
        pytest.skip("Can not run test via OpenWeather API")

    assert weather_said.data["thread_ts"] == "1234.5678"
    assert weather_said.data["username"] == "경기도 부천시 날씨"

    assert weather_said.data["text"] != "해당 주소는 찾을 수 없어요!"
    assert weather_said.data["text"] != "날씨 API 접근 중 에러가 발생했어요!"
    assert (
        weather_said.data["text"] != "검색 결과가 없어요! OpenWeather로 검색할 수 없는 곳 같아요!"
    )

    air_pollution_said = bot.call_queue.pop(0)

    assert air_pollution_said.method == "chat.postMessage"
    assert air_pollution_said.data["channel"] == "C1"
    assert result_pattern_re.match(air_pollution_said.data["text"]) is not None
    assert air_pollution_said.data["username"] == "경기도 부천시 대기질"


@pytest.mark.asyncio
async def test_weather_geocoding_error(
    bot_config, cache, response_mock, unavailable_address
):
    response_mock.get(
        URL("https://maps.googleapis.com/maps/api/geocode/json").with_query(
            region="kr",
            address=unavailable_address,
            key="DUMMY_GOOGLE_KEY",
        ),
        payload={"results": [], "status": "ZERO_RESULTS"},
    )

    bot_config.OPENWEATHER_API_KEY = "DUMMY_OPENWEATHER_KEY"
    bot_config.GOOGLE_API_KEY = "DUMMY_GOOGLE_KEY"

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
async def test_weather_openweather_error(
    bot_config, cache, response_mock, address
):
    response_mock.get(
        URL("https://maps.googleapis.com/maps/api/geocode/json").with_query(
            region="kr",
            address=address,
            key="DUMMY_GOOGLE_KEY",
        ),
        payload={
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
        },
    )
    response_mock.get(
        URL("https://api.openweathermap.org/data/2.5/weather").with_query(
            appid="DUMMY_OPENWEATHER_KEY",
            lat="37.5034138",
            lon="126.7660309",
            units="metric",
        ),
        payload=None,
        status=401,
    )
    response_mock.get(
        URL(
            "https://api.openweathermap.org/data/2.5/air_pollution"
        ).with_query(
            appid="DUMMY_OPENWEATHER_KEY",
            lat="37.5034138",
            lon="126.7660309",
        ),
        payload={},
        status=401,
    )

    bot_config.OPENWEATHER_API_KEY = "DUMMY_OPENWEATHER_KEY"
    bot_config.GOOGLE_API_KEY = "DUMMY_GOOGLE_KEY"

    bot = FakeBot(bot_config, cache=cache)
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")

    event = bot.create_message("C1", "U1", "1234.5678")

    async with bot.begin():
        await weather(bot, event, address)

    said = bot.call_queue.pop(0)

    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "날씨 API 접근 중 에러가 발생했어요!"
