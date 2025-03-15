from datetime import timedelta

import pytest
import pytest_asyncio
from more_itertools import flatten
from yarl import URL

from yui.apps.search.subway import REGION_TABLE
from yui.apps.search.subway import Result
from yui.apps.search.subway import body
from yui.apps.search.subway import busan_subway
from yui.apps.search.subway import daegu_subway
from yui.apps.search.subway import daejeon_subway
from yui.apps.search.subway import fetch_all_station_db
from yui.apps.search.subway import fetch_station_db
from yui.apps.search.subway import find_station_id
from yui.apps.search.subway import get_shortest_route
from yui.apps.search.subway import gwangju_subway
from yui.apps.search.subway import make_route_desc
from yui.apps.search.subway import on_start
from yui.apps.search.subway import refresh_db
from yui.apps.search.subway import subway
from yui.utils.datetime import now

from ...util import assert_crontab_match
from ...util import assert_crontab_spec


@pytest_asyncio.fixture(name="bot")
async def bot_with_cache(bot, cache):
    async with bot.use_cache(cache):
        yield bot


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
    assert_crontab_spec(refresh_db)


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
    assert_crontab_match(refresh_db, sunday + delta, expected=result)


@pytest.mark.asyncio
async def test_refresh_db(bot, monkeypatch):
    async def fake_fetch(bot_):
        assert bot is bot_

    monkeypatch.setattr(
        "yui.apps.search.subway.fetch_all_station_db",
        fake_fetch,
    )

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


@pytest.mark.asyncio
async def test_command_body(bot, start_name, goal_name):
    event = bot.create_message()

    await body(bot, event, "수도권", start_name, goal_name)
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert isinstance(said.data, dict)
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "아직 지하철 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!"
    )

    await fetch_station_db(
        bot,
        REGION_TABLE["수도권"][0],
        REGION_TABLE["수도권"][1],
    )

    await body(bot, event, "수도권", "서울", "서을")
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert isinstance(said.data, dict)
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "출발역과 도착역이 동일한 역인 것 같아요! (참고로 제가 인식한 역 이름은 '서울역' 이에요!)"
    )

    await body(bot, event, "수도권", "ASDF", goal_name)
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert isinstance(said.data, dict)
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "출발역으로 지정하신 역 이름을 찾지 못하겠어요!"

    await body(bot, event, "수도권", start_name, "ASDF")
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert isinstance(said.data, dict)
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "도착역으로 지정하신 역 이름을 찾지 못하겠어요!"

    await body(bot, event, "수도권", start_name, goal_name)
    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert isinstance(said.data, dict)
    assert said.data["channel"] == event.channel
    assert start_name in said.data["text"]
    assert goal_name in said.data["text"]


@pytest.mark.asyncio
async def test_branch_commands(bot, monkeypatch):
    event = bot.create_message()
    history = []

    async def fake_body(bot_, event_, region, start, end):
        history.append((bot_, event_, region, start, end))

    monkeypatch.setattr(
        "yui.apps.search.subway.body",
        fake_body,
    )

    await subway(bot, event, "수도권", "서울", "인천")
    result = history.pop(0)
    assert result[0] is bot
    assert result[1] is event
    assert result[2] == "수도권"
    assert result[3] == "서울"
    assert result[4] == "인천"

    await busan_subway(bot, event, "가야대", "수영")
    result = history.pop(0)
    assert result[0] is bot
    assert result[1] is event
    assert result[2] == "부산"
    assert result[3] == "가야대"
    assert result[4] == "수영"

    await daegu_subway(bot, event, "학정", "지산")
    result = history.pop(0)
    assert result[0] is bot
    assert result[1] is event
    assert result[2] == "대구"
    assert result[3] == "학정"
    assert result[4] == "지산"

    await gwangju_subway(bot, event, "상무", "소태")
    result = history.pop(0)
    assert result[0] is bot
    assert result[1] is event
    assert result[2] == "광주"
    assert result[3] == "상무"
    assert result[4] == "소태"

    await daejeon_subway(bot, event, "반석", "월평")
    result = history.pop(0)
    assert result[0] is bot
    assert result[1] is event
    assert result[2] == "대전"
    assert result[3] == "반석"
    assert result[4] == "월평"
