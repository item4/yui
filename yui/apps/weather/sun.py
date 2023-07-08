from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo

import aiohttp

from ...utils import json

TZ = ZoneInfo("Asia/Seoul")


async def get_emoji_by_sun(
    dt: datetime,
) -> Literal[":sunny:", ":crescent_moon:"]:
    async with aiohttp.ClientSession() as session, session.get(
        "https://api.sunrise-sunset.org/json",
        params={
            "lat": 37.558213,  # NOTE: 서울역
            "lng": 126.971354,  # NOTE: 서울역
            "formatted": 0,
            "date": dt.date().isoformat(),
        },
    ) as resp:
        data = await resp.json(loads=json.loads)
    result = data["results"]
    sunrise = datetime.fromisoformat(result["sunrise"]).astimezone(TZ)
    sunset = datetime.fromisoformat(result["sunset"]).astimezone(TZ)
    if sunrise <= dt < sunset:
        return ":sunny:"
    return ":crescent_moon:"
