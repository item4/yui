import datetime
from typing import Literal
from zoneinfo import ZoneInfo

import aiohttp

from ...utils import json
from ...utils.datetime import fromisoformat

TZ = ZoneInfo("Asia/Seoul")


async def get_emoji_by_sun(
    input: datetime.datetime,
) -> Literal[":sunny:", ":crescent_moon:"]:
    async with aiohttp.ClientSession() as session, session.get(
        "https://api.sunrise-sunset.org/json",
        params={
            "lat": 37.558213,  # NOTE: 서울역
            "lng": 126.971354,  # NOTE: 서울역
            "formatted": 0,
            "date": input.date().isoformat(),
        },
    ) as resp:
        data = await resp.json(loads=json.loads)
    result = data["results"]
    sunrise = fromisoformat(result["sunrise"])
    sunset = fromisoformat(result["sunset"])
    if sunrise <= input < sunset:
        return ":sunny:"
    return ":crescent_moon:"
