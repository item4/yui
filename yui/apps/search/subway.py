import asyncio
import logging
import re
from datetime import datetime

import aiohttp
import tossicat

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

PARENTHESES = re.compile(r"\(.+?\)")

logger = logging.getLogger(__name__)

TEMPLATE = "{}에서 {} {}행 열차에 탑승해서 {} 정거장을 지나 {}에서 내립니다.{}"
REGION_TABLE: dict[str, tuple[str, str]] = {
    "수도권": ("1000", "6.57"),
    "부산": ("7000", "4.21"),
    "대구": ("4000", "4.20"),
    "광주": ("5000", "4.9"),
    "대전": ("3000", "4.9"),
}


async def fetch_station_db(bot, service_region: str, api_version: str):
    name = f"subway-{service_region}-{api_version}"
    logger.info(f"fetch {name} start")

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
            "https://map.naver.com/p/api/subway/meta",
            params={
                "readPath": service_region,
                "version": api_version,
                "language": "ko",
                "style": "normal",
                "requestFile": "metaData.json",
                "caller": "NaverMapPcBetaWeb",
            },
        ) as resp,
    ):
        data = await resp.json(loads=json.loads)

    await bot.cache.set(f"SUBWAY_{service_region}_{api_version}", data)

    logger.info(f"fetch {name} end")


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
):
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
                "lang": "ko",
                "includeDetailOperation": "true",
                "departureTime": time.strftime("%Y-%m-%dT%H:%M:%S"),
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
            "출발역과 도착역이 동일한 역인 것 같아요!"
            f" (참고로 제가 인식한 역 이름은 '{e}'"
            " 이에요!)",
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

    text = ""

    paths = await get_shortest_route(service_region, start_id, end_id, now())

    if paths:
        duration = paths["duration"]
        fare = paths["fare"]
        distance = paths["distance"] / 1000
        steps = paths["legs"][0]["steps"]
        start_station_name = steps[0]["stations"][0]["displayName"]
        start_station_line = steps[0]["routes"][0]["name"]
        goal_station_name = steps[-1]["stations"][-1]["displayName"]
        goal_station_line = steps[-1]["routes"][0]["name"]

        text += "{} {}에서 {} {} 가는 노선을 안내드릴게요!\n\n".format(
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
            start_name = stations[0]["displayName"]
            line = routes[0]["longName"]
            direction = routes[0]["headsign"]
            station_count = sum(1 for r in stations if r["stop"]) - 1
            end_name = stations[-1]["displayName"]
            doors = platform["doors"]
            doors_list = ", ".join(doors) if doors else ""
            guide = ""
            if doors_list:
                guide = f" ({platform['type']['desc']}: {doors_list})"
            text += TEMPLATE.format(
                start_name,
                line,
                direction,
                station_count,
                end_name,
                guide,
            )
            text += "\n"

        text += (
            f"\n소요시간: {duration:,}분 / 거리: {distance:,.2f}㎞"
            f" / 요금(카드 기준): {fare:,}원"
        )

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
