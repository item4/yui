import pytest
from aiohttp.client_exceptions import ClientConnectorCertificateError
from aiohttp.client_reqrep import ConnectionKey

from yui.apps.weather.exceptions import WeatherResponseError
from yui.apps.weather.weather import WeatherRecord
from yui.apps.weather.weather import get_weather_by_keyword
from yui.utils.datetime import datetime
from yui.utils.datetime import now


@pytest.mark.asyncio
async def test_get_weather_datetime_is_correct(
    google_api_key,
    address,
):
    weather_data = await get_weather_by_keyword(address)

    assert weather_data.observed_at < now()


@pytest.mark.asyncio
async def test_get_weather_with_bad_response(response_mock, address):
    response_mock.get(
        "https://item4.net/api/weather/",
        payload={},
        status=400,
    )

    with pytest.raises(WeatherResponseError, match="Bad HTTP Response"):
        await get_weather_by_keyword(address)


@pytest.mark.asyncio
async def test_get_weather_with_bad_json(response_mock, address):
    response_mock.get(
        "https://item4.net/api/weather/",
        body="[}",
        status=200,
    )

    with pytest.raises(WeatherResponseError, match="JSON 파싱 실패"):
        await get_weather_by_keyword(address)


@pytest.mark.asyncio
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


def test_weather_record_as_str():
    weather = WeatherRecord(
        name="부천",
        location="경기도 부천시 원미구 중동",
        temperature=25.60,
        humidity=50,
        atmospheric=1013.0,
        wind_velocity=1.5,
        wind_direction="NE",
        is_rain="Rain",
        rain_15=0.50,
        rain_day=3.4567,
        observed_at=datetime(2024, 2, 2, 12, 34, 56),
    )
    assert weather.as_str() == (
        "[경기도 부천시 원미구 중동 / 12시 34분 기준] 강수 예(15분: 0.5㎜ / 일일: 3.46㎜) / 기온: 25.6℃"
        " / 바람: NE 1.5㎧ / 습도: 50% / 해면기압: 1013㍱\n\n추천 의상: 반팔티, 얇은 셔츠, 반바지, 면바지"
    )

    weather = WeatherRecord(
        name="부천",
        location="경기도 부천시 원미구 중동",
        temperature=-25.60,
        humidity=50,
        atmospheric=1013.0,
        wind_velocity=1.5,
        wind_direction="NE",
        is_rain="Rain",
        rain_15=0.50,
        rain_day=3.4567,
        observed_at=datetime(2024, 2, 2, 12, 34, 56),
    )
    assert weather.as_str() == (
        "[경기도 부천시 원미구 중동 / 12시 34분 기준] 강설 예(15분: 0.5㎜ / 일일: 3.46㎜) / 기온: -25.6℃ /"
        " 바람: NE 1.5㎧ / 습도: 50% / 해면기압: 1013㍱\n\n추천 의상: 패딩, 두꺼운 코트, 목도리, 기모제품"
    )

    weather = WeatherRecord(
        name="부천",
        location="경기도 부천시 원미구 중동",
        temperature=15.60,
        humidity=50,
        atmospheric=1013.0,
        wind_velocity=1.5,
        wind_direction="NE",
        is_rain="Clear",
        rain_15=None,
        rain_day=None,
        observed_at=datetime(2024, 2, 2, 12, 34, 56),
    )
    assert weather.as_str() == (
        "[경기도 부천시 원미구 중동 / 12시 34분 기준] 기온: 15.6℃"
        " / 바람: NE 1.5㎧ / 습도: 50% / 해면기압: 1013㍱\n\n"
        "추천 의상: 얇은 재킷, 가디건, 간절기 야상, 맨투맨, 니트, 살구색 스타킹"
    )

    weather = WeatherRecord(
        name="부천",
        location="경기도 부천시 원미구 중동",
        temperature=15.60,
        humidity=50,
        atmospheric=1013.0,
        wind_velocity=1.5,
        wind_direction="NE",
        is_rain="Unavailable",
        rain_15=None,
        rain_day=None,
        observed_at=datetime(2024, 2, 2, 12, 34, 56),
    )
    assert weather.as_str() == (
        "[경기도 부천시 원미구 중동 / 12시 34분 기준] 강수 확인 불가 / 기온: 15.6℃"
        " / 바람: NE 1.5㎧ / 습도: 50% / 해면기압: 1013㍱\n\n"
        "추천 의상: 얇은 재킷, 가디건, 간절기 야상, 맨투맨, 니트, 살구색 스타킹"
    )

    weather = WeatherRecord(
        name="부천",
        location="경기도 부천시 원미구 중동",
        temperature=15.60,
        humidity=50,
        atmospheric=1013.0,
        wind_velocity=1.5,
        wind_direction="NE",
        is_rain="Unknown",
        rain_15=None,
        rain_day=None,
        observed_at=datetime(2024, 2, 2, 12, 34, 56),
    )
    assert weather.as_str() == (
        "[경기도 부천시 원미구 중동 / 12시 34분 기준] 강수 알 수 없음 / 기온: 15.6℃"
        " / 바람: NE 1.5㎧ / 습도: 50% / 해면기압: 1013㍱"
        "\n\n추천 의상: 얇은 재킷, 가디건, 간절기 야상, 맨투맨, 니트, 살구색 스타킹"
    )
