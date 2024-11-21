import logging
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from ....box import box
from ....utils.datetime import now
from .commons import cleanup_by_event_logs
from .commons import collect_history_from_channel

box.assert_config_required("USER_TOKEN", str)
box.assert_channels_required("auto_cleanup_targets")


@box.cron("0,10,20,30,40,50 * * * *")
async def cleanup_channels(bot, sess: AsyncSession):
    logger = logging.getLogger("yui.apps.manage.cleanup.tasks.cleanup_channels")
    channels = bot.config.CHANNELS.get("auto_cleanup_targets", [])

    if not channels:
        return

    time_limit = now() - timedelta(hours=12)
    ts = str(int(time_limit.timestamp()))

    logger.info(f"Delete messages before {ts}")
    for channel in channels:
        logger.info(f"Start channel cleanup: {channel}")
        deleted = await cleanup_by_event_logs(
            bot,
            sess,
            channel,
            ts,
            bot.config.USER_TOKEN,
        )
        logger.info(f"Finish channel cleanup: {channel}, {deleted} deleted")


@box.cron("5 * * * *")
async def get_old_history(bot, sess: AsyncSession):
    logger = logging.getLogger("yui.apps.manage.cleanup.tasks.get_old_history")
    channels = bot.config.CHANNELS.get("auto_cleanup_targets", [])

    for channel in channels:
        logger.info(f"Start collect message in channel: {channel}")
        collected = await collect_history_from_channel(bot, channel, sess)
        logger.info(
            f"Finish collect message in channel: {channel},"
            f" {collected} collected",
        )
