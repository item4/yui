import datetime
import functools
import random

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
    holiday = await get_holiday_name(today)

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

        for say in says:
            await monday_dog_say(text=say)


async def get_holiday_name(dt: datetime.datetime):
    url = 'http://api.manana.kr/calendar/{date}/holiday/kr.json'.format(
        date=dt.strftime('%Y/%m/%d')
    )

    async with client_session() as session:
        async with session.get(url) as resp:
            holidays = ujson.loads(await resp.text())

    if holidays:
        return holidays[0]['name']
