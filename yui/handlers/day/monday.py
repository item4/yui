import functools
import random

import aiohttp

from .util import get_holiday_name
from ...box import box
from ...command import C
from ...util import now

box.assert_config_required('TDCPROJECT_KEY', str)
box.assert_config_required('MONDAY_DOG_LIMIT', int)
box.assert_channel_required('general')


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

        for say in says[:min(bot.config.MONDAY_DOG_LIMIT, len(says))]:
            await monday_dog_say(text=say)


