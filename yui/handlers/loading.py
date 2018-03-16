import datetime
import functools
import random

import ujson

from ..box import box
from ..command import C
from ..event import Message
from ..session import client_session
from ..util import now


def weekend_loading_percent(now: datetime.datetime) -> float:
    weekday = now.weekday()
    if weekday in [5, 6]:
        return 100.0
    monday = (now - datetime.timedelta(days=weekday)).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    delta = now - monday
    return delta.total_seconds() / (5*24*60*60) * 100


@box.crontab('0 0,8,12,18,22 * * 1-5')
async def auto_weekend_loading(bot):
    now_dt = now()
    percent = weekend_loading_percent(now_dt)
    await bot.say(
        C.general.get(),
        f'주말로딩… {percent:.2f}%'
    )


@box.crontab('0 0 * * 6')
async def auto_weekend_start(bot):
    await bot.say(
        C.general.get(),
        f'주말이에요! 즐거운 주말 되세요!'
    )


@box.crontab('0 0 * * 1')
async def auto_weekend_end(bot):
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
            '월' * random.randint(10, 30) + '…' + ''.join(
                random.choice(['?', '!']) for x in range(random.randint(3, 10))
            ),
            '(하지만 {}이라 쉬는 날이었다고 한다)'.format(holiday)
        ]
        for say in says:
            await monday_dog_say(text=say)
    else:
        says = [
            '월' * random.randint(30, 120),
            ''.join(
                '월' * random.randint(1, 6) + '!' * random.randint(1, 3)
                for x in range(40)
            ),
            '월요일' * random.randint(10, 40),
        ]
        random.shuffle(says)

        for say in says:
            await monday_dog_say(text=say)


@box.command('주말로딩')
async def weekend_loading(bot, event: Message):
    """
    주말로딩

    주말까지 얼마나 남았는지 출력합니다.

    `{PREFIX}주말로딩`

    """

    now_dt = now()
    percent = weekend_loading_percent(now_dt)
    if percent == 100.0:
        await bot.say(
            event.channel,
            '주말이에요! 즐거운 주말 되세요!'
        )
    else:
        await bot.say(
            event.channel,
            f'주말로딩… {percent:.2f}%'
        )


async def get_holiday_name(dt: datetime.datetime):
    url = 'http://api.manana.kr/calendar/{date}/holiday/kr.json'.format(
        date=dt.strftime('%Y/%m/%d')
    )

    async with client_session() as session:
        async with session.get(url) as resp:
            holidays = ujson.loads(await resp.text())

    if holidays:
        return holidays[0]['name']
