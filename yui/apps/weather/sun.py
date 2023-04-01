import datetime
from typing import Literal

import aiohttp

from ...utils import json


async def get_emoji_by_sun(
    input: datetime.datetime,
    offset: int,
    lat: float,
    lng: float,
) -> Literal[":sunny:", ":crescent_moon:"]:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.sunrise-sunset.org/json",
            params={
                "lat": lat,
                "lng": lng,
                "formatted": 0,
                "date": input.date().isoformat(),
            },
        ) as resp:
            data = await resp.json(loads=json.loads)
    result = data["results"]
    tz = datetime.timezone(datetime.timedelta(seconds=offset))
    sunrise = datetime.datetime.fromisoformat(result["sunrise"]).astimezone(tz)
    sunset = datetime.datetime.fromisoformat(result["sunset"]).astimezone(tz)
    if sunrise <= input < sunset:
        return ":sunny:"
    return ":crescent_moon:"
