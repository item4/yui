import asyncio
import logging
import operator
import re
from datetime import datetime
from typing import Final
from typing import TypedDict

import aiohttp
import tossicat
from more_itertools import ilen

from ...box import box
from ...command import argument
from ...command import option
from ...event import Message
from ...event import YuiSystemStart
from ...transform import choice
from ...utils import json
from ...utils.datetime import now
from ...utils.fuzz import ratio
from ...utils.http import USER_AGENT

TEMPLATE: Final = (
    "{start_station}에서 {line_name} {direction}행 열차에 탑승해서 {station_count} 정거장을 지나"
    " {goal_station}에서 내립니다.{extra_guides}"
)
REGION_TABLE: Final[dict[str, tuple[str, str]]] = {
    "수도권": ("1000", "6.61"),
    "부산": ("7000", "4.24"),
    "대구": ("4000", "4.22"),
    "광주": ("5000", "4.10"),
    "대전": ("3000", "4.10"),
}

PARENTHESES = re.compile(r"\(.+?\)")

logger = logging.getLogger(__name__)


class PlatformType(TypedDict):
    desc: str


class Platform(TypedDict):
    doors: list[str]
    type: PlatformType


class Station(TypedDict):
    displayName: str
    stop: bool


class Route(TypedDict):
    name: str
    longName: str
    headsign: str
    platform: Platform


class Step(TypedDict):
    type: str
    stations: list[Station]
    routes: list[Route]


class Leg(TypedDict):
    steps: list[Step]


class Result(TypedDict):
    duration: int
    fare: int
    distance: int
    legs: list[Leg]


async def fetch_station_db(bot, service_region: str, api_version: str):
    name = f"subway-{service_region}-{api_version}"
    logger.info("fetch %s start", name)

    async with (
        aiohttp.ClientSession(
            headers={
                "User-Agent": USER_AGENT,
                "Referer": (
                    f"https://map.naver.com/p/subway/{service_region}/-/-/-"
                ),
            },
        ) as session,
        session.get(
            "https://apis.map.naver.com/SubwayProvide.xml",
            params={
                "readPath": service_region,
                "version": api_version,
                "language": "ko",
                "style": "normal",
                "requestFile": "metaData.json",
                "caller": "pcweb_v5",
            },
        ) as resp,
    ):
        data = await resp.json(loads=json.loads)

    await bot.cache.set(f"SUBWAY_{service_region}_{api_version}", data)

    logger.info("fetch %s end", name)


async def fetch_all_station_db(bot):
    tasks = []
    for service_region, api_version in REGION_TABLE.values():
        tasks.append(
            asyncio.create_task(
                fetch_station_db(bot, service_region, api_version),
            ),
        )
    await asyncio.wait(tasks)


async def get_shortest_route(
    service_region: str,
    start_id: str,
    end_id: str,
    time: datetime,
) -> Result:
    async with (
        aiohttp.ClientSession(
            headers={
                "User-Agent": USER_AGENT,
                "Referer": (
                    f"https://map.naver.com/p/subway/{service_region}/-/-/-"
                ),
            },
        ) as session,
        session.get(
            "https://map.naver.com/p/api/pubtrans/subway-directions",
            params={
                "start": start_id,
                "goal": end_id,
                "departureTime": time.strftime("%Y-%m-%dT%H:%M:%S") + "+09:00",
            },
        ) as resp,
    ):
        result = await resp.json(loads=json.loads)

    try:
        return result["paths"][0]
    except (KeyError, IndexError) as e:
        raise ValueError from e


@box.on(YuiSystemStart)
async def on_start(bot):
    logger.info("on_start subway")
    await fetch_all_station_db(bot)
    return True


@box.cron("0 3 * * *")
async def refresh_db(bot):
    logger.info("refresh subway")
    await fetch_all_station_db(bot)


def find_station_id(
    data: list[dict[str, str]],
    start: str,
    end: str,
) -> tuple[str | None, str | None]:
    find_start = None
    find_start_ratio = -1
    find_end = None
    find_end_ratio = -1
    for x in data:
        name = PARENTHESES.sub("", x["name"])
        start_ratio = ratio(name, start)
        end_ratio = ratio(name, end)
        if find_start_ratio < start_ratio:
            find_start = x
            find_start_ratio = start_ratio
        if find_end_ratio < end_ratio:
            find_end = x
            find_end_ratio = end_ratio

    start_id = (
        find_start["id"] if find_start and find_start_ratio >= 40 else None
    )
    end_id = find_end["id"] if find_end and find_end_ratio >= 40 else None
    if start_id == end_id and start_id is not None and find_start:
        raise ValueError(find_start["name"])
    return start_id, end_id


def make_route_desc(data: Result) -> str:
    duration = data["duration"]
    fare = data["fare"]
    distance = data["distance"] / 1000
    steps = data["legs"][0]["steps"]
    start_station_name = steps[0]["stations"][0]["displayName"]
    start_station_line = steps[0]["routes"][0]["name"]
    goal_station_name = steps[-1]["stations"][-1]["displayName"]
    goal_station_line = steps[-1]["routes"][0]["name"]

    result = "{} {}에서 {} {} 가는 노선을 안내드릴게요!\n\n".format(
        start_station_line,
        start_station_name,
        goal_station_line,
        tossicat.postfix(goal_station_name, "(으)로"),
    )
    for step in steps:
        if step["type"] != "SUBWAY":
            continue
        routes = step["routes"]
        stations = step["stations"]
        platform = routes[0]["platform"]
        start_station = stations[0]["displayName"]
        line_name = routes[0]["longName"]
        direction = routes[0]["headsign"]
        station_count = ilen(filter(operator.itemgetter("stop"), stations)) - 1
        goal_station = stations[-1]["displayName"]
        doors = platform["doors"]
        doors_list = ", ".join(doors) if doors else ""
        extra_guides = ""
        if doors_list:
            extra_guides = f" ({platform['type']['desc']}: {doors_list})"
        result += TEMPLATE.format(
            start_station=start_station,
            line_name=line_name,
            direction=direction,
            station_count=station_count,
            goal_station=goal_station,
            extra_guides=extra_guides,
        )
        result += "\n"

    result += f"\n소요시간: {duration:,}분 / 거리: {distance:,.2f}㎞ / 요금(카드 기준): {fare:,}원"

    return result


async def body(bot, event: Message, region: str, start: str, end: str):
    service_region, api_version = REGION_TABLE[region]

    data = await bot.cache.get(f"SUBWAY_{service_region}_{api_version}")
    if data is None:
        await bot.say(
            event.channel,
            "아직 지하철 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!",
        )
        return

    try:
        start_id, end_id = find_station_id(data[0]["realInfo"], start, end)
    except ValueError as e:
        await bot.say(
            event.channel,
            f"출발역과 도착역이 동일한 역인 것 같아요! (참고로 제가 인식한 역 이름은 '{e}' 이에요!)",
        )
        return

    if not start_id:
        await bot.say(
            event.channel,
            "출발역으로 지정하신 역 이름을 찾지 못하겠어요!",
        )
        return
    if not end_id:
        await bot.say(
            event.channel,
            "도착역으로 지정하신 역 이름을 찾지 못하겠어요!",
        )
        return

    result = await get_shortest_route(service_region, start_id, end_id, now())
    text = make_route_desc(result)

    await bot.say(event.channel, text)


@box.command("지하철", ["전철", "subway"])
@option(
    "--region",
    "-r",
    "--지역",
    default="수도권",
    transform_func=choice(list(REGION_TABLE.keys())),
    transform_error="지원되는 지역이 아니에요",
)
@argument("start", count_error="출발역을 입력해주세요")
@argument("end", count_error="도착역을 입력해주세요")
async def subway(bot, event: Message, region: str, start: str, end: str):
    """
    전철/지하철의 예상 소요시간 및 탑승 루트 안내

    `{PREFIX}지하철 부천 선릉`
    (수도권 전철 부천역에서 선릉역까지 가는 가장 빠른 방법 안내)
    `{PREFIX}지하철 --region 부산 가야대 노포`
    (부산 전철 가야대역 출발 노포역 도착으로 조회)

    """

    await body(bot, event, region, start, end)


@box.command("부산지하철", ["부산전철"])
@argument("start", count_error="출발역을 입력해주세요")
@argument("end", count_error="도착역을 입력해주세요")
async def busan_subway(bot, event: Message, start: str, end: str):
    """
    부산 전철/지하철의 예상 소요시간 및 탑승 루트 안내

    `{PREFIX}지하철 --region 부산` 의 단축 명령어입니다.
    자세한 도움말은 `{PREFIX}help 지하철` 을 참조해주세요.

    """

    await body(bot, event, "부산", start, end)


@box.command("대구지하철", ["대구전철"])
@argument("start", count_error="출발역을 입력해주세요")
@argument("end", count_error="도착역을 입력해주세요")
async def daegu_subway(bot, event: Message, start: str, end: str):
    """
    대구 전철/지하철의 예상 소요시간 및 탑승 루트 안내

    `{PREFIX}지하철 --region 대구` 의 단축 명령어입니다.
    자세한 도움말은 `{PREFIX}help 지하철` 을 참조해주세요.

    """

    await body(bot, event, "대구", start, end)


@box.command("광주지하철", ["광주전철"])
@argument("start", count_error="출발역을 입력해주세요")
@argument("end", count_error="도착역을 입력해주세요")
async def gwangju_subway(bot, event: Message, start: str, end: str):
    """
    광주 전철/지하철의 예상 소요시간 및 탑승 루트 안내

    `{PREFIX}지하철 --region 광주` 의 단축 명령어입니다.
    자세한 도움말은 `{PREFIX}help 지하철` 을 참조해주세요.

    """

    await body(bot, event, "광주", start, end)


@box.command("대전지하철", ["대전전철"])
@argument("start", count_error="출발역을 입력해주세요")
@argument("end", count_error="도착역을 입력해주세요")
async def daejeon_subway(bot, event: Message, start: str, end: str):
    """
    대전 전철/지하철의 예상 소요시간 및 탑승 루트 안내

    `{PREFIX}지하철 --region 대전` 의 단축 명령어입니다.
    자세한 도움말은 `{PREFIX}help 지하철` 을 참조해주세요.

    """

    await body(bot, event, "대전", start, end)
