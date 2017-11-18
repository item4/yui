import os

import pytest

from yui.handlers.aqi import (
    AQIRecord,
    get_aqi,
    get_aqi_description,
    get_geometric_info_by_address,
)


@pytest.fixture()
def fx_aqi_api_token():
    token = os.getenv('AQI_API_TOKEN')
    if not token:
        pytest.skip('Can not test this without AQI_API_TOKEN envvar')
    return token


@pytest.fixture()
def fx_google_api_key():
    key = os.getenv('GOOGLE_API_KEY')
    if not key:
        pytest.skip('Can not test this without GOOGLE_API_KEY envvar')
    return key


@pytest.mark.asyncio
async def test_get_geometric_info_by_address(fx_google_api_key):
    full_address, lat, lng = await get_geometric_info_by_address(
        '부천',
        fx_google_api_key,
    )

    assert full_address == '대한민국 경기도 부천시'
    assert lat == 37.5034138
    assert lng == 126.7660309

    full_address, lat, lng = await get_geometric_info_by_address(
        '서울',
        fx_google_api_key,
    )

    assert full_address == '대한민국 서울특별시 서울특별시'
    assert lat == 37.566535
    assert lng == 126.9779692

    with pytest.raises(IndexError):
        await get_geometric_info_by_address(
            'ㅁㄴㅇㄹ1234' * 10,
            fx_google_api_key,
        )


@pytest.mark.asyncio
async def test_get_aqi(fx_aqi_api_token):
    result = await get_aqi(37.5034138, 126.9779692, fx_aqi_api_token)

    assert isinstance(result, AQIRecord)


def test_get_aqi_description():
    assert get_aqi_description(0).startswith('좋음')
    assert get_aqi_description(50).startswith('좋음')
    assert get_aqi_description(51).startswith('보통')
    assert get_aqi_description(100).startswith('보통')
    assert get_aqi_description(101).startswith('민감군 영향')
    assert get_aqi_description(150).startswith('민감군 영향')
    assert get_aqi_description(151).startswith('나쁨')
    assert get_aqi_description(200).startswith('나쁨')
    assert get_aqi_description(201).startswith('매우 나쁨')
    assert get_aqi_description(300).startswith('매우 나쁨')
    assert get_aqi_description(301).startswith('위험')
    assert get_aqi_description(400).startswith('위험')
