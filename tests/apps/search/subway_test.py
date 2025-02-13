from datetime import timedelta

import pytest
import pytest_asyncio
from more_itertools import flatten
from yarl import URL

from yui.apps.search.subway import REGION_TABLE
from yui.apps.search.subway import fetch_all_station_db
from yui.apps.search.subway import find_station_id
from yui.apps.search.subway import get_shortest_route
from yui.apps.search.subway import on_start
from yui.apps.search.subway import refresh_db
from yui.utils.datetime import now

from ...util import FakeBot


@pytest_asyncio.fixture()
async def bot(cache) -> FakeBot:
    return FakeBot(cache=cache)


@pytest.fixture(scope="session")
def station_data():
    return [
        {
            "id": "1",
            "name": "서울",
        },
        {
            "id": "2",
            "name": "인천",
        },
        {
            "id": "3",
            "name": "구로",
        },
        {
            "id": "4",
            "name": "신도림",
        },
    ]


@pytest.fixture(scope="session")
def time():
    return (now() + timedelta(hours=24)).replace(
        hour=9,
        minute=0,
        second=0,
        microsecond=0,
    )


@pytest.mark.asyncio
async def test_fetch_all_station_db(bot):
    async with bot.begin():
        for service_region, api_version in REGION_TABLE.values():
            data = await bot.cache.get(f"SUBWAY_{service_region}_{api_version}")
            assert data is None

        await fetch_all_station_db(bot)

        for service_region, api_version in REGION_TABLE.values():
            data = await bot.cache.get(f"SUBWAY_{service_region}_{api_version}")
            assert isinstance(data, list)
            assert isinstance(data[0], dict)


@pytest.mark.asyncio
async def test_get_shortest_route_fail(response_mock, time):
    url = URL(
        "https://map.naver.com/p/api/pubtrans/subway-directions",
    ).with_query(
        start="161",
        goal="133",
        lang="ko",
        includeDetailOperation="true",
        departureTime=time.strftime("%Y-%m-%dT%H:%M:%S"),
    )
    response_mock.get(
        url,
        payload={"error": "error"},
    )
    response_mock.get(
        url,
        payload={"paths": []},
    )
    with pytest.raises(ValueError):
        await get_shortest_route(
            REGION_TABLE["수도권"][0],
            "161",  # 1호선 인천역
            "133",  # 1호선 서울역
            time,
        )
    with pytest.raises(ValueError):
        await get_shortest_route(
            REGION_TABLE["수도권"][0],
            "161",  # 1호선 인천역
            "133",  # 1호선 서울역
            time,
        )


@pytest.mark.asyncio
async def test_get_shortest_route(time):
    try:
        result = await get_shortest_route(
            REGION_TABLE["수도권"][0],
            "161",  # 1호선 인천역
            "133",  # 1호선 서울역
            time,
        )
    except ValueError:
        pytest.skip("API server is not available")
        return

    assert isinstance(result, dict)
    assert result["duration"]
    assert result["fare"]
    assert result["distance"]
    assert result["legs"]
    assert result["legs"][0]["steps"]


@pytest.mark.asyncio
async def test_on_start(bot, monkeypatch):
    async def fake_fetch(bot_):
        assert bot is bot_

    monkeypatch.setattr(
        "yui.apps.search.subway.fetch_all_station_db",
        fake_fetch,
    )

    async with bot.begin():
        assert await on_start(bot)


def test_refresh_db_spec():
    assert refresh_db.has_valid_spec


@pytest.mark.parametrize(
    ("delta", "result"),
    flatten(
        [
            (timedelta(days=x, hours=0), False),
            (timedelta(days=x, hours=2), False),
            (timedelta(days=x, hours=3), True),
            (timedelta(days=x, hours=3, minutes=30), False),
            (timedelta(days=x, hours=4), False),
        ]
        for x in range(7)
    ),
)
def test_refresh_db_match(sunday, delta, result):
    assert refresh_db.match(sunday + delta) is result


@pytest.mark.asyncio
async def test_refresh_db(bot, monkeypatch):
    async def fake_fetch(bot_):
        assert bot is bot_

    monkeypatch.setattr(
        "yui.apps.search.subway.fetch_all_station_db",
        fake_fetch,
    )

    async with bot.begin():
        await refresh_db(bot)


def test_find_station_id(station_data):
    assert find_station_id(station_data, "서울", "인천") == ("1", "2")
    assert find_station_id(station_data, "스울", "온촌") == ("1", "2")
    assert find_station_id(station_data, "신도림", "독도") == ("4", None)
    assert find_station_id(station_data, "독도", "구로") == (None, "3")
    assert find_station_id(station_data, "독도", "독도") == (None, None)

    with pytest.raises(ValueError, match="인천"):
        find_station_id(station_data, "인천", "인천")
