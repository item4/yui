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

    logger.info("Delete messages before %s", ts)
    for channel in channels:
        logger.info("Start channel cleanup: %s", channel)
        deleted = await cleanup_by_event_logs(
            bot,
            sess,
            channel,
            ts,
            bot.config.USER_TOKEN,
        )
        logger.info("Finish channel cleanup: %s, %d deleted", channel, deleted)


@box.cron("5 * * * *")
async def get_old_history(bot, sess: AsyncSession):
    logger = logging.getLogger("yui.apps.manage.cleanup.tasks.get_old_history")
    channels = bot.config.CHANNELS.get("auto_cleanup_targets", [])

    for channel in channels:
        logger.info("Start collect message in channel: %s", channel)
        collected = await collect_history_from_channel(bot, channel, sess)
        logger.info(
            "Finish collect message in channel: %s, %d collected",
            channel,
            collected,
        )
