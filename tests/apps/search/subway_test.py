from datetime import timedelta

import pytest
import pytest_asyncio
from more_itertools import flatten
from yarl import URL

from yui.apps.search.subway import REGION_TABLE
from yui.apps.search.subway import Result
from yui.apps.search.subway import fetch_all_station_db
from yui.apps.search.subway import find_station_id
from yui.apps.search.subway import get_shortest_route
from yui.apps.search.subway import make_route_desc
from yui.apps.search.subway import on_start
from yui.apps.search.subway import refresh_db
from yui.utils.datetime import now

from ...util import FakeBot


@pytest_asyncio.fixture()
async def bot(cache) -> FakeBot:
    return FakeBot(cache=cache)


@pytest.fixture(scope="session")
def start_id():
    return "133"


@pytest.fixture(scope="session")
def start_name():
    return "서울역"


@pytest.fixture(scope="session")
def goal_id():
    return "1914"


@pytest.fixture(scope="session")
def goal_name():
    return "판교"


@pytest.fixture(scope="session")
def station_data(start_id, start_name, goal_id, goal_name):
    return [
        {
            "id": start_id,
            "name": start_name,
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
        {
            "id": goal_id,
            "name": goal_name,
        },
    ]


@pytest.fixture(scope="session")
def result_data(start_name, goal_name) -> Result:
    return {
        "duration": 42,
        "distance": 25811,
        "fare": 3500,
        "legs": [
            {
                "steps": [
                    {
                        "type": "SUBWAY",
                        "stations": [
                            {
                                "displayName": start_name,
                                "stop": True,
                            },
                            {
                                "displayName": "회현역",
                                "stop": True,
                            },
                            {
                                "displayName": "명동역",
                                "stop": True,
                            },
                            {
                                "displayName": "충무로역",
                                "stop": True,
                            },
                        ],
                        "routes": [
                            {
                                "name": "4호선",
                                "longName": "수도권 4호선(진접-오이도)",
                                "platform": {
                                    "type": {
                                        "desc": "빠른환승",
                                    },
                                    "doors": ["5-1"],
                                },
                                "headsign": "진접",
                            },
                        ],
                    },
                    {
                        "type": "WALKING",
                        "stations": [],
                        "routes": [],
                    },
                    {
                        "type": "SUBWAY",
                        "stations": [
                            {
                                "displayName": "충무로역",
                                "stop": True,
                            },
                            {
                                "displayName": "동대입구역",
                                "stop": True,
                            },
                            {
                                "displayName": "약수역",
                                "stop": True,
                            },
                            {
                                "displayName": "금호역",
                                "stop": True,
                            },
                            {
                                "displayName": "옥수역",
                                "stop": True,
                            },
                            {
                                "displayName": "압구정역",
                                "stop": True,
                            },
                            {
                                "displayName": "신사역",
                                "stop": True,
                            },
                        ],
                        "routes": [
                            {
                                "name": "3호선",
                                "longName": "수도권 3호선(대화-오금)",
                                "platform": {
                                    "type": {
                                        "desc": "빠른환승",
                                    },
                                    "doors": ["2-1"],
                                },
                                "headsign": "오금",
                            },
                        ],
                    },
                    {
                        "type": "WALKING",
                        "stations": [],
                        "routes": [],
                    },
                    {
                        "type": "SUBWAY",
                        "stations": [
                            {
                                "displayName": "신사역",
                                "stop": True,
                            },
                            {
                                "displayName": "논현역",
                                "stop": True,
                            },
                            {
                                "displayName": "신논현역",
                                "stop": True,
                            },
                            {
                                "displayName": "강남역",
                                "stop": True,
                            },
                            {
                                "displayName": "양재역",
                                "stop": True,
                            },
                            {
                                "displayName": "양재시민의숲역",
                                "stop": True,
                            },
                            {
                                "displayName": "청계산입구역",
                                "stop": True,
                            },
                            {
                                "displayName": f"{goal_name}역",
                                "stop": True,
                            },
                        ],
                        "routes": [
                            {
                                "name": "신분당선",
                                "longName": "수도권 신분당선(신사-광교)",
                                "platform": {
                                    "type": {
                                        "desc": "빠른하차",
                                    },
                                    "doors": ["1-1", "4-2"],
                                },
                                "headsign": "광교",
                            },
                        ],
                    },
                ],
            },
        ],
    }


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
async def test_get_shortest_route_fail(response_mock, time, start_id, goal_id):
    url = URL(
        "https://map.naver.com/p/api/pubtrans/subway-directions",
    ).with_query(
        start=start_id,
        goal=goal_id,
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
            start_id,
            goal_id,
            time,
        )
    with pytest.raises(ValueError):
        await get_shortest_route(
            REGION_TABLE["수도권"][0],
            start_id,
            goal_id,
            time,
        )


@pytest.mark.asyncio
async def test_get_shortest_route(time, start_id, goal_id):
    try:
        result = await get_shortest_route(
            REGION_TABLE["수도권"][0],
            start_id,
            goal_id,
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


def test_find_station_id(station_data, start_id):
    assert find_station_id(station_data, "서울", "인천") == (start_id, "2")
    assert find_station_id(station_data, "스울", "온촌") == (start_id, "2")
    assert find_station_id(station_data, "신도림", "독도") == ("4", None)
    assert find_station_id(station_data, "독도", "구로") == (None, "3")
    assert find_station_id(station_data, "독도", "독도") == (None, None)

    with pytest.raises(ValueError, match="인천"):
        find_station_id(station_data, "인천", "인천")

    with pytest.raises(ValueError, match="인천"):
        find_station_id(station_data, "잉천", "인천")


def test_make_route_desc(result_data):
    assert (
        make_route_desc(result_data)
        == """\
4호선 서울역에서 신분당선 판교역으로 가는 노선을 안내드릴게요!

서울역에서 수도권 4호선(진접-오이도) 진접행 열차에 탑승해서 3 정거장을 지나 충무로역에서 내립니다. (빠른환승: 5-1)
충무로역에서 수도권 3호선(대화-오금) 오금행 열차에 탑승해서 6 정거장을 지나 신사역에서 내립니다. (빠른환승: 2-1)
신사역에서 수도권 신분당선(신사-광교) 광교행 열차에 탑승해서 7 정거장을 지나 판교역에서 내립니다. (빠른하차: 1-1, 4-2)

소요시간: 42분 / 거리: 25.81㎞ / 요금(카드 기준): 3,500원"""
    )
