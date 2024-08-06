import pytest
from yarl import URL

from yui.apps.weather.exceptions import WeatherResponseError
from yui.apps.weather.geo import get_geometric_info_by_address


@pytest.mark.parametrize(
    ("keyword", "expected_full_address", "expected_lat", "expected_lng"),
    [
        ("부천", "경기도 부천시", 37.5038683, 126.7874615),
        ("서울", "서울특별시", 37.550263, 126.9970831),
        # 한국이 아니면 국가명이 붙는다.
        ("카와고에", "일본 사이타마현 가와고에시", 35.9251335, 139.4858042),
    ],
)
@pytest.mark.asyncio()
async def test_get_geometric_info_by_address(
    google_api_key,
    keyword,
    expected_full_address,
    expected_lat,
    expected_lng,
):
    full_address, lat, lng = await get_geometric_info_by_address(
        keyword,
        google_api_key,
    )

    assert full_address == expected_full_address
    assert (lat, lng) == pytest.approx((expected_lat, expected_lng), abs=1e-1)


@pytest.mark.asyncio()
async def test_get_weather_wrong_geometric_info(
    response_mock,
    unavailable_address,
):
    key = "XXX"
    response_mock.get(
        URL("https://maps.googleapis.com/maps/api/geocode/json").with_query(
            region="kr",
            address=unavailable_address,
            key=key,
        ),
        payload={
            "results": [],
        },
    )
    with pytest.raises(IndexError):
        await get_geometric_info_by_address(
            unavailable_address,
            key,
        )


@pytest.mark.asyncio()
async def test_get_weather_google_427(
    response_mock,
    unavailable_address,
):
    key = "XXX"
    response_mock.get(
        URL("https://maps.googleapis.com/maps/api/geocode/json").with_query(
            region="kr",
            address=unavailable_address,
            key=key,
        ),
        payload={
            "results": [],
        },
        status=427,
    )
    with pytest.raises(WeatherResponseError):
        await get_geometric_info_by_address(
            unavailable_address,
            key,
        )
