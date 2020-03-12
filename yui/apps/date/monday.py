import functools
import random

import aiohttp

import tossi

from .utils import get_holiday_names
from ...box import box
from ...command import C
from ...utils.datetime import now

box.assert_channel_required('general')


@box.cron('0 0 * * 1')
async def monday_dog(bot):
    name = getattr(bot.config, 'MONDAY_DOG_NAME', '월요일을 알리며 짖는 개')
    icon = getattr(
        bot.config, 'MONDAY_DOG_ICON', 'https://i.imgur.com/UtBQSLl.jpg',
    )
    monday_dog_say = functools.partial(
        bot.api.chat.postMessage,
        channel=C.general.get(),
        as_user=False,
        username=name,
        icon_url=icon,
    )
    today = now()
    holidays = None
    try:
        holidays = await get_holiday_names(today)
    except aiohttp.client_exceptions.ClientOSError:
        pass

    if holidays:
        says = [
            '월' * random.randint(3, 10)
            + '…'
            + ''.join(
                random.choice(['?', '!']) for x in range(random.randint(2, 4))
            ),
            '(하지만 {} 쉬는 날이었다고 한다)'.format(tossi.postfix(holidays[0], '(이)라'),),
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
