import pytest

from yui.apps.weather.exceptions import WeatherResponseError
from yui.apps.weather.geo import get_geometric_info_by_address
from yui.apps.weather.weather import get_weather_by_coordinate
from yui.utils import json
from yui.utils.datetime import fromtimestampoffset
from yui.utils.datetime import now


@pytest.mark.asyncio
async def test_get_weather_datetime_is_correct(
    google_api_key, openweather_api_key, address
):
    full_address, lat, lng = await get_geometric_info_by_address(
        address,
        google_api_key,
    )
    weather_data = await get_weather_by_coordinate(
        lat,
        lng,
        openweather_api_key,
    )

    # don't add or remove offset in timestamp
    dt = fromtimestampoffset(
        timestamp=weather_data.timestamp,
        offset=weather_data.timezone,
    )

    assert dt.timestamp() < now().timestamp()


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
