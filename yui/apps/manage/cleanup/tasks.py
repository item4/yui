import asyncio
import datetime
import random
import time

from more_itertools import mark_ends

from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import Select
from sqlalchemy.sql.expression import func

from .commons import cleanup_by_event_logs
from .models import EventLog
from ....bot import APICallError
from ....box import box
from ....command import Cs
from ....utils.report import report


box.assert_config_required('OWNER_USER_TOKEN', str)
box.assert_channels_required('auto_cleanup_targets')

LOGS = set[tuple[str, str]]


@box.cron('*/10 * * * *')
async def cleanup_channels(bot, sess):
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
        await asyncio.sleep(5)


@box.cron('0 */1 * * *')
async def add_missing_logs(bot, sess):
    try:
        channels = Cs.auto_cleanup_targets.gets()
    except KeyError:
        return
    all_logs: LOGS = set()
    for is_first, is_last, channel in mark_ends(channels):
        logs: LOGS = set()
        try:
            latest = sess.execute(
                Select([func.min(EventLog.ts)]).where(
                    EventLog.channel == channel.id
                )
            ).scalar()
        except NoResultFound:
            latest = None
        has_more = True
        cursor = None
        while has_more and len(logs) < 400:
            try:
                resp = await bot.api.conversations.history(
                    channel,
                    cursor=cursor,
                    latest=latest,
                )
            except APICallError as e:
                await report(bot, e.tb, exception=e)
                break

            history = resp.body
            if not history['ok']:
                break
            has_more = history['has_more']
            if has_more:
                cursor = history['response_metadata']['next_cursor']
            messages = {
                (m.get('reply_count', 0), m['ts']) for m in history['messages']
            }

            while messages:
                reply_count, ts = messages.pop()
                if reply_count:
                    has_more_replies = True
                    replies_cursor = None
                    while has_more_replies:
                        try:
                            r = await bot.api.conversations.replies(
                                channel,
                                cursor=replies_cursor,
                                ts=ts,
                            )
                        except APICallError as e:
                            await report(bot, e.tb, exception=e)
                            break
                        replies = r.body
                        if not replies['ok']:
                            break
                        has_more_replies = replies['has_more']
                        if has_more_replies:
                            replies_cursor = replies['response_metadata'][
                                'next_cursor'
                            ]
                        messages |= {
                            (m.get('reply_count', 0), m['ts'])
                            for m in replies.get('messages', [])
                        }
                        if has_more_replies:
                            await asyncio.sleep(random.uniform(2.0, 5.0))

                logs.add((channel.id, ts))

            if has_more:
                await asyncio.sleep(random.uniform(2.0, 5.0))

        all_logs |= logs

        if not is_last:
            await asyncio.sleep(random.uniform(2.0, 5.0))

    if all_logs:
        with sess.begin():
            sess.execute(
                Insert(EventLog)
                .values([{'channel': c, 'ts': t} for c, t in all_logs])
                .on_conflict_do_nothing()
            )
