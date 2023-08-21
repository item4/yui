import pytest
from aiohttp.client_exceptions import ClientConnectorCertificateError
from aiohttp.client_reqrep import ConnectionKey

from yui.apps.weather.exceptions import WeatherResponseError
from yui.apps.weather.weather import get_weather_by_keyword
from yui.utils.datetime import now


@pytest.mark.asyncio()
async def test_get_weather_datetime_is_correct(
    google_api_key,
    address,
):
    weather_data = await get_weather_by_keyword(address)

    assert weather_data.observed_at < now()


@pytest.mark.asyncio()
async def test_get_weather_with_bad_response(response_mock, address):
    response_mock.get(
        "https://item4.net/api/weather/",
        payload={},
        status=400,
    )

    with pytest.raises(WeatherResponseError, match="Bad HTTP Response"):
        await get_weather_by_keyword(address)


@pytest.mark.asyncio()
async def test_get_weather_with_bad_json(response_mock, address):
    response_mock.get(
        "https://item4.net/api/weather/",
        body="[}",
        status=200,
    )

    with pytest.raises(WeatherResponseError, match="JSON 파싱 실패"):
        await get_weather_by_keyword(address)


@pytest.mark.asyncio()
async def test_get_weather_with_expired_cert(response_mock, address):
    response_mock.get(
        "https://item4.net/api/weather/",
        payload={},
        exception=ClientConnectorCertificateError(
            ConnectionKey("item4.net", 433, True, True, None, None, None),
            Exception("test"),
        ),
    )

    with pytest.raises(WeatherResponseError, match="인증서 만료"):
        await get_weather_by_keyword(address)
