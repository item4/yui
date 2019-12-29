import asyncio
import datetime
import time

from .commons import cleanup_by_event_logs
from ....box import box
from ....command import Cs

box.assert_config_required('OWNER_USER_TOKEN', str)
box.assert_channels_required('auto_cleanup_targets')
box.assert_users_required('force_cleanup')

COOLTIME = datetime.timedelta(minutes=5)


@box.cron('*/10 * * * *')
async def cleanup_channels(bot, sess):
    try:
        channels = Cs.auto_cleanup_targets.gets()
    except KeyError:
        return

    naive_now = datetime.datetime.now()
    time_limit = naive_now - datetime.timedelta(hours=5)
    ts = str(time.mktime(time_limit.timetuple()))

    for channel in channels:
        await cleanup_by_event_logs(bot, sess, channel, ts)
        await asyncio.sleep(5)
