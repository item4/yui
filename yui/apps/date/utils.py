import datetime
from typing import Final

import aiohttp

from ...utils import json

WEEKEND: Final = frozenset({5, 6})


class APIDoesNotSupport(Exception):
    pass


async def get_holiday_names(date: datetime.date) -> list[str]:
    url = "https://item4.net/api/holiday"
    async with (
        aiohttp.ClientSession() as session,
        session.get(
            "{}/{}".format(url, date.strftime("%Y/%m/%d")),
        ) as resp,
    ):
        if resp.status == 200:
            return await resp.json(loads=json.loads)
    raise APIDoesNotSupport


def weekend_loading_percent(dt: datetime.datetime) -> float:
    weekday = dt.weekday()
    if weekday in WEEKEND:
        return 100.0
    monday = (dt - datetime.timedelta(days=weekday)).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    delta = dt - monday
    return delta.total_seconds() / (5 * 24 * 60 * 60) * 100


def weekend_loading_box(percent: float) -> str:
    total_block_count = 20
    if percent >= 100:
        return "[" + "■" * total_block_count + "]"

    black_blocks = "■" * int(percent // 5)
    white_blocks = "□" * (total_block_count - len(black_blocks))
    return "[" + black_blocks + white_blocks + "]"
