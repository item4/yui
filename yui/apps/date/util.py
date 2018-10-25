import datetime
from typing import Any, Dict, Optional

import ujson

from ...session import client_session


async def get_event_days(
    *,
    api_key: str,
    year: str,
    month: str = None,
    day: str = None,
    type: str = None,
) -> Dict[str, Any]:
    url = 'https://apis.sktelecom.com/v1/eventday/days'
    params = {
        'year': year,
    }

    if month:
        params['month'] = month

    if day:
        params['day'] = day

    if type:
        params['type'] = type

    headers = {
        'TDCProjectKey': api_key,
    }

    async with client_session() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            return await resp.json(loads=ujson.loads)


async def get_holiday_name(
    api_key: str,
    dt: datetime.datetime,
) -> Optional[str]:
    year, month, day = dt.strftime('%Y/%m/%d').split('/')
    data = await get_event_days(
        api_key=api_key,
        year=year,
        month=month,
        day=day,
        type='h',
    )

    if data['results']:
        return data['results'][0]['name']
    return None


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
