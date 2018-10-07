import asyncio
import datetime
import logging
import time

from ..bot import APICallError
from ..box import box
from ..command import Cs

box.assert_config_required('OWNER_USER_TOKEN', str)
box.assert_channels_required('auto_cleanup_targets')

logger = logging.getLogger(__name__)


@box.crontab('*/10 * * * *')
async def cleanup_channels(bot):
    try:
        channels = Cs.auto_cleanup_targets.get()
    except KeyError:
        return

    naive_now = datetime.datetime.now()
    time_limit = naive_now - datetime.timedelta(hours=6)

    latest_ts = str(time.mktime(time_limit.timetuple()))
    logger.debug(f'latest_ts: {latest_ts}')

    for channel in channels:
        logger.debug(f'channel {channel.name} start')
        history = await bot.api.channels.history(
            channel,
            count=100,
            latest=latest_ts,
            unreads=True,
        )

        if history['ok']:
            logger.debug(f'channel history: {len(history["messages"])}')
            for message in history['messages']:
                try:
                    r = await bot.api.chat.delete(
                        channel,
                        message['ts'],
                        token=bot.config.OWNER_USER_TOKEN,
                    )
                    logger.debug(f'message {message["ts"]} delete: {r}')
                except APICallError:
                    logger.debug(f'message {message} fail to delete')
                    break
        logger.debug(f'channel {channel.name} end')

        await asyncio.sleep(1)
