import asyncio
import math
import urllib.parse
from datetime import datetime
from typing import Any

import aiohttp
import aiohttp.client_exceptions

import async_timeout

from attrs import define
from attrs import field

from fuzzywuzzy import fuzz

from ...box import box
from ...command import argument
from ...command import option
from ...event import Message
from ...types.slack.attachment import Attachment
from ...utils import json
from ...utils.fuzz import match


MIN_RATIO = 60
DOW = [
    "일요일",
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "기타",
]
DATE_FORMAT = "%Y년 %m월 %d일 %H시"


def fix_url(url: str) -> str:
    if "blog.naver.com" in url or ".tistory.com" in url or ".blog.me" in url:
        if url.startswith("http"):
            url = url.split("//", 1)[1]
        return f"https://{url}"
    elif url.startswith("http://") or url.startswith("https://"):
        return url
    return f"http://{url}"


def convert_released_dt(input: str) -> str:
    input = input.replace("-", "").replace("T", "").replace(":", "")
    try:
        return datetime.strptime(input, "%Y%m%d%H%M%S").strftime(DATE_FORMAT)
    except ValueError:
        return str(input)


@define(frozen=True, hash=True, eq=True)
class Sub:

    maker: str
    episode_num: str
    url: str = field(converter=fix_url)
    released_at: str = field(converter=convert_released_dt)


def print_time(t: str) -> str:
    return "{}:{}".format(t[:2], t[2:])


def encode_url(u: str) -> str:
    prefix = ""
    if u.startswith("http://"):
        prefix = "http://"
    elif u.startswith("https://"):
        prefix = "https://"
    return prefix + "/".join(
        urllib.parse.quote(c) for c in u.replace(prefix, "").split("/")
    )


def make_sub_list(data: set[Sub]) -> list[Attachment]:
    result: list[Attachment] = []

    if data:
        for sub in reversed(
            sorted(list(data), key=lambda x: (x.episode_num, x.released_at))
        ):
            num = "완결" if sub.episode_num == 9999 else f"{sub.episode_num}화"
            name = sub.maker
            url = sub.url
            date = sub.released_at
            if date:
                fallback = f"{num} {date} {name} {url}"
                text = f"{num} {date} {url}"
            else:
                fallback = f"{num} {name} {url}"
                text = f"{num} {url}"
            result.append(
                Attachment(fallback=fallback, author_name=name, text=text)
            )
    else:
        result.append(
            Attachment(fallback="자막 제작자가 없습니다.", text="자막 제작자가 없습니다.")
        )

    return result


@box.command("sub", ["자막", "애니자막"])
@option("--finished/--on-air", "--종영/--방영", "--완결/--방송", "--fin/--on", "-f/-o")
@argument("title", nargs=-1, concat=True, count_error="애니 제목을 입력해주세요")
async def sub(bot, event: Message, finished: bool, title: str):
    """
    애니메이션 자막을 검색합니다

    OHLI와 애니시아 자막 편성표에서 주어진 제목과 가장 근접한 제목의 애니를 검색하여 보여줍니다.

    방영중 애니 검색은 기본적으로 OHLI의 자막 목록에서 fuzzy search 후, OHLI에서 제공하는
    ALIAS를 기준으로 삼아 애니시아의 자막 목록에서 검색합니다. 따라서 OHLI와 애니시아의 애니명이
    다른 경우에는 검색이 가능하지만, OHLI에 아예 없는 애니는 검색이 불가능합니다.

    종영 애니 포함 검색은 OHLI만을 검색합니다. OHLI의 검색 API를 이용하기 때문에
    fuzzy search를 지원하지 않습니다.

    `{PREFIX}sub 이나즈마 일레븐` (제목이 `'이나즈마 일레븐'` 에 근접하는 것을 검색)
    `{PREFIX}sub 나 히 아` (제목이 `'나 히 아'` 에 근접하는 것을 검색)
    `{PREFIX}sub 히로아카` (OHLI의 애니 별칭 목록에 있는것은 별칭으로도 검색 가능)
    `{PREFIX}sub --완결 aldnoah` (제목에 `'aldnoah'`가 들어가는 애니 + 완결애니를 검색)

    """

    if finished:
        await search_finished(bot, event, title)
    else:
        await search_on_air(bot, event, title)


async def get_ohli_now_json(timeout: float) -> list[list[dict[str, Any]]]:
    async with async_timeout.timeout(timeout):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.OHLI.moe/timetable/list/now"
            ) as resp:
                return await resp.json(loads=json.loads)


async def get_ohli_caption_list(i, timeout: float) -> set[Sub]:
    result: set[Sub] = set()
    async with async_timeout.timeout(timeout):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.OHLI.moe/timetable/cap?i={i}"
            ) as resp:
                data = await resp.json(loads=json.loads)

    for sub in data:
        episode_num = sub["s"]
        if int(math.ceil(episode_num)) == int(episode_num):
            episode_num = int(episode_num)
        result.add(
            Sub(
                maker=sub["n"],
                episode_num=str(episode_num),
                url=sub["a"],
                released_at=sub["d"],
            )
        )

    return result


async def get_anissia_weekly_json(
    week: int,
    timeout: float,
) -> list[dict[str, Any]]:
    async with async_timeout.timeout(timeout):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://anissia.net/api/anime/schedule/{week}"
            ) as resp:
                return await resp.json(loads=json.loads)


async def get_annissia_caption_list_json(
    anime_no: int,
    timeout: float,
) -> list[dict]:
    async with async_timeout.timeout(timeout):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://anissia.net/api/anime/caption/animeNo/{anime_no}"
            ) as resp:
                return await resp.json(loads=json.loads)


def select_animes_from_ohli(title, ohli_all):
    title = title.lower()
    data = []
    for w, weekday_list in enumerate(ohli_all):
        for ani in weekday_list:
            ani["week"] = w
            ani["ratio"] = max(
                [
                    match(title, ani["s"].lower()),
                    max(match(title, a["s"].lower()) for a in ani["n"]),
                ]
            )

            if any(
                [
                    title in ani["s"].lower(),
                    *[title in a["s"].lower() for a in ani["n"]],
                ]
            ):
                ani["ratio"] += 10
            data.append(ani)

    results = []
    first = 0
    for ani in sorted(data, key=lambda x: -x["ratio"]):
        if ani["ratio"] < MIN_RATIO:
            break
        if not first:
            first = ani["ratio"]
        elif first - 20 > ani["ratio"]:
            break
        results.append(ani)
    return results


def select_one_anime_from_anissia(ohli_ani, anissia_week):
    for ani in anissia_week:
        ani["ratio"] = max(
            match(alias["s"].lower(), ani["subject"].lower())
            for alias in ohli_ani["n"]
        )

        if ani["subject"] == ohli_ani["t"]:
            ani["ratio"] += 5
        if fuzz.ratio(ani["website"], ohli_ani["l"]) > 90:
            ani["ratio"] += 10

    return max(anissia_week, key=lambda x: x["ratio"])


async def search_on_air(bot, event: Message, title: str, timeout: float = 2.5):
    try:
        ohli_all = await get_ohli_now_json(timeout)
    except asyncio.TimeoutError:
        await bot.say(
            event.channel,
            "OHLI 서버가 너무 느려요! 자막 검색이 곤란하니 나중에 다시 시도해주세요!",
        )
        return

    matched = select_animes_from_ohli(title, ohli_all)

    if not matched:
        await bot.say(event.channel, "해당 제목의 애니는 찾을 수 없어요!")
        return

    for ohli_ani in matched:
        try:
            captions = await get_ohli_caption_list(ohli_ani["i"], timeout)
        except asyncio.TimeoutError:
            captions = set()

        try:
            anissia_week = await get_anissia_weekly_json(
                ohli_ani["week"],
                timeout,
            )
        except asyncio.TimeoutError:
            anissia_week = []

        use_anissia = False
        anissia_ani = None
        if anissia_week:
            anissia_ani = select_one_anime_from_anissia(
                ohli_ani,
                anissia_week,
            )
            if anissia_ani["ratio"] > MIN_RATIO:
                try:
                    anissia_subs = await get_annissia_caption_list_json(
                        anissia_ani["animeNo"],
                        timeout,
                    )
                except asyncio.TimeoutError:
                    anissia_subs = []
                use_anissia = bool(anissia_subs)
                for sub in anissia_subs:
                    url = encode_url(sub["website"])
                    captions.add(
                        Sub(
                            maker=sub["name"],
                            episode_num=sub["episode"],
                            url=url,
                            released_at=sub["updDt"],
                        )
                    )

        title = ohli_ani["s"]
        dow = DOW[ohli_ani["week"]]
        time = print_time(ohli_ani["t"])
        url = fix_url(ohli_ani["l"])
        if use_anissia and anissia_ani:
            genres = anissia_ani["genres"]
            fallback = f"*{title}* ({dow} {time} / {genres} / {url})"
            text = f"{dow} {time} / {genres} / Source: OHLI & Anissia"
        else:
            fallback = f"*{title}* ({dow} {time} / {url})"
            text = f"{dow} {time} / Source: OHLI"

        attachments: list[Attachment] = [
            Attachment(
                fallback=fallback,
                title=title,
                title_link=url,
                text=text,
                thumb_url=ohli_ani["img"] or None,
            ),
        ]
        attachments.extend(make_sub_list(captions))

        await bot.api.chat.postMessage(
            channel=event.channel,
            attachments=attachments,
            thread_ts=event.ts,
        )


async def search_finished(
    bot,
    event: Message,
    title: str,
    timeout: float = 2.5,
):
    try:
        async with async_timeout.timeout(timeout):
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://ohli.moe/timetable/search",
                    params={"query": title},
                ) as resp:
                    data = await resp.json(loads=json.loads)
    except asyncio.TimeoutError:
        await bot.say(event.channel, "OHLI 서버 상태가 좋지 않아요! 다음에 시도해주세요!")
        return

    if data:
        await bot.say(
            event.channel,
            f"완결애니를 포함하여 OHLI DB에서 검색한 결과 총 {len(data):,}개의 애니가 검색되었어요!",
            thread_ts=event.event_ts,
        )
        for ani in data:
            try:
                captions = await get_ohli_caption_list(ani["i"], timeout)
            except asyncio.TimeoutError:
                captions = set()

            attachments: list[Attachment] = [
                Attachment(
                    fallback="*{title}* ({url})".format(
                        title=ani["s"],
                        url=ani["l"],
                    ),
                    title=ani["s"],
                    title_link=fix_url(ani["l"]) if ani["l"] else None,
                    thumb_url=ani["img"] or None,
                ),
            ]
            attachments.extend(make_sub_list(captions))

            await bot.api.chat.postMessage(
                channel=event.channel,
                attachments=attachments,
                thread_ts=event.event_ts,
            )
    else:
        await bot.say(
            event.channel,
            "해당 제목의 완결 애니는 찾을 수 없어요!",
        )
