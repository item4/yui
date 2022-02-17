from sqlalchemy.dialects.postgresql import Insert

from .models import EventLog
from ....bot import APICallError
from ....box import box
from ....command import Cs
from ....event import Hello
from ....event import Message


@box.on(Hello)
async def get_old_history(bot, sess):
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
                with sess.begin():
                    sess.execute(
                        Insert(EventLog)
                        .values(channel=channel.id, ts=message['ts'])
                        .on_conflict_do_nothing()
                    )
                if ts is None:
                    ts = message['ts']
                else:
                    ts = min(ts, message['ts'])

    return True


@box.on(Message, subtype='*')
async def make_log(bot, event: Message, sess):
    try:
        channels = Cs.auto_cleanup_targets.gets()
    except KeyError:
        return True

    if event.subtype == 'message_deleted':
        return True

    if event.channel in channels:
        with sess.begin():
            sess.execute(
                Insert(EventLog)
                .values(channel=event.channel.id, ts=event.ts)
                .on_conflict_do_nothing()
            )
    return True
