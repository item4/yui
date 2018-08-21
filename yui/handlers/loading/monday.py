import datetime
import functools
import random
from typing import Optional

import aiohttp

import ujson

from yui.box import box
from yui.command import C
from yui.session import client_session
from yui.util import now


@box.crontab('0 0 * * 1')
async def monday_dog(bot):
    monday_dog_say = functools.partial(
        bot.api.chat.postMessage,
        channel=C.general.get(),
        as_user=False,
        username='월요일을 알리는 개새끼',
        icon_url='https://i.imgur.com/UtBQSLl.jpg',
    )
    today = now()
    holiday = None
    try:
        holiday = await get_holiday_name(bot.config.TDCPROJECT_KEY, today)
    except aiohttp.client_exceptions.ClientOSError:
        pass

    if holiday:
        says = [
            '월' * random.randint(5, 15) + '…' + ''.join(
                random.choice(['?', '!']) for x in range(random.randint(3, 10))
            ),
            '(하지만 {}이라 쉬는 날이었다고 한다)'.format(holiday)
        ]
        for say in says:
            await monday_dog_say(text=say)
    else:
        says = [
            '월' * random.randint(60, 220),
            ''.join(
                '월' * random.randint(1, 6) + '!' * random.randint(1, 3)
                for x in range(40)
            ),
            '월요일' * random.randint(30, 70),
        ]
        random.shuffle(says)

        for say in says[:bot.config.get('MONDAY_DOG_LIMIT', len(says))]:
            await monday_dog_say(text=say)


async def get_holiday_name(
    api_key: str,
    dt: datetime.datetime,
) -> Optional[str]:
    year, month, day = dt.strftime('%Y/%m/%d').split('/')
    url = 'https://apis.sktelecom.com/v1/eventday/days'
    params = {
        'year': year,
        'month': month,
        'day': day,
    }
    headers = {
        'TDCProjectKey': api_key,
    }

    async with client_session() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            data = await resp.json(loads=ujson.loads)

    if data['results']:
        return data['results'][0]['name']
    return None
