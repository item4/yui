import asyncio
import datetime
import time

from ..bot import APICallError
from ..box import box
from ..command import Cs
from ..util import now


@box.crontab('*/10 * * * *')
async def cleanup_channels(bot):
    channels = Cs.auto_cleanup_targets.get()

    latest_ts = str(
        time.mktime((now() - datetime.timedelta(hours=3)).timetuple())
    )

    for channel in channels:
        history = await bot.api.channels.history(
            channel,
            count=100,
            latest=latest_ts,
            unreads=True,
        )

        if history['ok']:
            for message in history['messages']:
                try:
                    await bot.api.chat.delete(
                        channel,
                        message['ts'],
                        bot.config.OWNER_USER_TOKEN,
                    )
                except APICallError:
                    break

        await asyncio.sleep(1)
