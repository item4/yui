import pytest

from yui.apps.weather.air import get_air_pollution_by_coordinate
from yui.apps.weather.air import get_aqi_description
from yui.apps.weather.air import get_emoji_by_aqi
from yui.apps.weather.exceptions import WeatherResponseError
from yui.utils import json


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
    "level, expected",
    [
        (1, ":smile:"),
        (2, ":smiley:"),
        (3, ":neutral_face:"),
        (4, ":mask:"),
        (5, ":skull_and_crossbones:"),  # API Spec은 5단계가 최대입니다.
        (42, ":interrobang:"),  # 예외 처리
    ],
)
def test_get_emoji_by_aqi(level, expected):
    assert get_emoji_by_aqi(level) == expected
