import datetime
from typing import List

from ...session import client_session
from ...utils import json


class APIDoesNotSupport(Exception):
    pass


async def get_holiday_names(dt: datetime.datetime) -> List[str]:
    url = 'https://item4.net/api/holiday'
    async with client_session() as session:
        async with session.get(
            '{}/{}'.format(url, dt.strftime('%Y/%m/%d'))
        ) as resp:
            if resp.status == 200:
                return await resp.json(loads=json.loads)
    raise APIDoesNotSupport


def weekend_loading_percent(dt: datetime.datetime) -> float:
    weekday = dt.weekday()
    if weekday in [5, 6]:
        return 100.0
    monday = (dt - datetime.timedelta(days=weekday)).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    delta = dt - monday
    return delta.total_seconds() / (5*24*60*60) * 100
