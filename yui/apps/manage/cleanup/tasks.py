import datetime
import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession

from .commons import cleanup_by_event_logs
from .commons import collect_history_from_channel
from ....box import box


box.assert_config_required("USER_TOKEN", str)
box.assert_channels_required("auto_cleanup_targets")

LOGS = set[tuple[str, str]]


@box.cron("0,10,20,30,40,50 * * * *")
async def cleanup_channels(bot, sess: AsyncSession):
    logger = logging.getLogger(
        "yui.apps.manage.cleanup.tasks.cleanup_channels"
    )
    try:
        channels = bot.config.CHANNELS["auto_cleanup_targets"]
    except KeyError:
        logger.info("No auto cleanup targets. skip.")
        return

    naive_now = datetime.datetime.now()
    time_limit = naive_now - datetime.timedelta(hours=12)
    ts = str(time.mktime(time_limit.timetuple()))

    logger.info(f"Delete messages before {ts}")
    for channel in channels:
        logger.info(f"Start channel cleanup: {channel}")
        deleted = await cleanup_by_event_logs(
            bot,
            sess,
            channel,
            ts,
            bot.config.OWNER_USER_TOKEN,
        )
        logger.info(f"Finish channel cleanup: {channel}, {deleted} deleted")


@box.cron("0 * * * *")
async def get_old_history(bot, sess: AsyncSession):
    logger = logging.getLogger("yui.apps.manage.cleanup.tasks.get_old_history")
    try:
        channels = bot.config.CHANNELS["auto_cleanup_targets"]
    except KeyError:
        logger.info("No auto cleanup targets. skip.")
        return

    for channel in channels:
        logger.info(f"Start collect message in channel: {channel}")
        collected = await collect_history_from_channel(bot, channel, sess)
        logger.info(
            f"Finish collect message in channel: {channel}"
            f", {collected} collected"
        )
