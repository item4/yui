import pytest

from yui.apps.weather.geo import get_geometric_info_by_address
from yui.utils import json


@pytest.mark.parametrize(
    "keyword,expected_full_address,expected_lat,expected_lng",
    [
        ("부천", "경기도 부천시", 37.5034138, 126.7660309),
        ("서울", "서울특별시", 37.566535, 126.9779692),
        # 한국이 아니면 국가명이 붙는다.
        ("카와고에", "일본 사이타마현 가와고에시", 35.9251335, 139.4858042),
    ],
)
@pytest.mark.asyncio
async def test_get_geometric_info_by_address(
    google_api_key, keyword, expected_full_address, expected_lat, expected_lng
):
    full_address, lat, lng = await get_geometric_info_by_address(
        keyword,
        google_api_key,
    )

    assert full_address == expected_full_address
    assert lat == expected_lat
    assert lng == expected_lng


@pytest.mark.asyncio
async def test_get_weather_wrong_geometric_info(
    response_mock, unavailable_address
):
    key = "XXX"
    response_mock.get(
        "https://maps.googleapis.com/maps/api/geocode/json"
        f"?region=kr&address={unavailable_address}&key=XXX",
        body=json.dumps(
            {
                "results": [],
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    with pytest.raises(IndexError):
        await get_geometric_info_by_address(
            unavailable_address,
            key,
        )
