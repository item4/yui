import asyncio
import datetime
import random
import time

from sqlalchemy.dialects.postgresql import Insert

from .commons import cleanup_by_event_logs
from .models import EventLog
from ....box import box
from ....command import Cs

box.assert_config_required('OWNER_USER_TOKEN', str)
box.assert_channels_required('auto_cleanup_targets')
box.assert_users_required('force_cleanup')


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


@box.cron('0 0,6,12,28 * * *')
async def add_missing_logs(bot, sess):
    try:
        channels = Cs.auto_cleanup_targets.gets()
    except KeyError:
        return True
    logs: list[dict] = []
    try:
        for channel in channels:
            has_more = True
            cursor = None
            count = 0
            while has_more and count < 1000:
                resp = await bot.api.conversations.history(
                    channel,
                    cursor=cursor,
                )

                history = resp.body
                if not history['ok']:
                    break
                has_more = history['has_more']
                if has_more:
                    cursor = history['response_metadata']['next_cursor']
                messages = history['messages']

                while messages:
                    message = messages.pop(0)
                    reply_count = message.get('reply_count', 0)
                    if reply_count:
                        has_more_replies = True
                        replies_cursor = None
                        while has_more_replies:
                            r = await bot.api.conversations.replies(
                                channel,
                                cursor=replies_cursor,
                                ts=message['ts'],
                            )
                            replies = r.body
                            if not replies['ok']:
                                break
                            has_more_replies = replies['has_more']
                            if has_more_replies:
                                replies_cursor = replies['response_metadata'][
                                    'next_cursor'
                                ]
                            messages += replies.get('messages', [])
                            await asyncio.sleep(random.uniform(2.0, 5.0))

                    logs.append({'channel': channel.id, 'ts': message['ts']})
                    count += 1

                await asyncio.sleep(random.uniform(2.5, 7.5))
            await asyncio.sleep(random.uniform(2.5, 7.5))
    except:  # noqa
        pass

    if logs:
        with sess.begin():
            sess.execute(
                Insert(EventLog).values(logs).on_conflict_do_nothing()
            )

    return True
