import datetime
import time

from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.ext.asyncio import AsyncSession

from .commons import cleanup_by_event_logs
from .models import EventLog
from ....bot import APICallError
from ....box import box
from ....command import Cs


box.assert_config_required('OWNER_USER_TOKEN', str)
box.assert_channels_required('auto_cleanup_targets')

LOGS = set[tuple[str, str]]


@box.cron('*/10 * * * *')
async def cleanup_channels(bot, sess: AsyncSession):
    try:
        channels = Cs.auto_cleanup_targets.gets()
    except KeyError:
        return

    naive_now = datetime.datetime.now()
    time_limit = naive_now - datetime.timedelta(hours=12)
    ts = str(time.mktime(time_limit.timetuple()))

    for channel in channels:
        await cleanup_by_event_logs(
            bot,
            sess,
            channel,
            ts,
            bot.config.OWNER_USER_TOKEN,
        )


@box.cron('0 * * * *')
async def get_old_history(bot, sess: AsyncSession):
    try:
        channels = Cs.auto_cleanup_targets.gets()
    except KeyError:
        return True

    for channel in channels:
        ts = None
        while True:
            try:
                resp = await bot.api.conversations.history(
                    channel.id,
                    latest=ts,
                )
            except APICallError:
                break

            history = resp.body
            if not history['ok']:
                break

            messages = history['messages']
            while messages:
                message = messages.pop(0)
                reply_count = message.get('reply_count', 0)
                if reply_count:
                    try:
                        r = await bot.api.conversations.replies(
                            channel,
                            ts=message['ts'],
                        )
                    except APICallError:
                        pass
                    else:
                        messages += r.body.get('messages', [])
                async with sess.begin():
                    await sess.execute(
                        Insert(EventLog)
                        .values(channel=channel.id, ts=message['ts'])
                        .on_conflict_do_nothing()
                    )
                if ts is None:
                    ts = message['ts']
                else:
                    ts = min(ts, message['ts'])

    return True
