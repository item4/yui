import asyncio
import random

from .models import EventLog
from ....box import box
from ....command import Cs
from ....event import ChatterboxSystemStart
from ....event import Message


@box.on(Message, subtype='*')
async def make_log(bot, event: Message, sess):
    try:
        channels = Cs.auto_cleanup_targets.gets()
    except KeyError:
        return True

    if event.subtype == 'message_deleted':
        return True

    if event.channel in channels:
        log = EventLog(channel=event.channel.id, ts=event.ts)
        with sess.begin():
            sess.add(log)
    return True


@box.on(ChatterboxSystemStart)
async def add_missing_logs(bot, sess):
    try:
        channels = Cs.auto_cleanup_targets.gets()
    except KeyError:
        return True
    logs: list[EventLog] = []
    for channel in channels:
        has_more = True
        cursor = None
        while has_more:
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
                        await asyncio.sleep(random.uniform(1.0, 3.0))

                logs.append(EventLog(channel=channel.id, ts=message['ts']))

            await asyncio.sleep(random.uniform(1.0, 3.0))
        await asyncio.sleep(random.uniform(5.0, 15.0))

    if logs:
        with sess.begin():
            sess.add_all(logs)

    return True
