from typing import Optional

from .models import EventLog
from ....bot import APICallError
from ....types.channel import Channel
from ....utils.report import report


async def cleanup_by_event_logs(
    bot,
    sess,
    channel: Channel,
    ts: str,
    token: Optional[str],
    count: Optional[int] = None,
) -> int:
    deleted = 0
    logs = (
        sess.query(EventLog)
        .filter(
            EventLog.channel == channel.id,
            EventLog.ts <= ts,
        )
        .order_by(EventLog.ts.desc())
    )
    if count:
        logs = logs.limit(count)
    for log in logs:  # type: EventLog
        try:
            resp = await bot.api.chat.delete(
                log.channel,
                log.ts,
                token=token,
            )
        except APICallError as e:
            await report(bot, exception=e)
            return deleted
        ok = resp.body['ok']
        if ok or (not ok and resp.body['error'] == 'message_not_found'):
            deleted += ok
            with sess.begin():
                sess.delete(log)

    return deleted


async def cleanup_by_history(
    bot,
    channel: Channel,
    ts: str,
    token: Optional[str],
    minimum: int = 100,
    as_user: bool = False,
) -> int:
    deleted = 0
    deletable = True
    while deletable and deleted < minimum:
        try:
            resp = await bot.api.conversations.history(
                channel,
                latest=ts,
            )
        except APICallError as e:
            await report(bot, exception=e)
            break
        history = resp.body
        deletable = False
        if history['ok']:
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
                    except APICallError as e:
                        await report(bot, exception=e)
                        break
                    messages += r.body.get('messages', [])
                try:
                    res = await bot.api.chat.delete(
                        channel,
                        message['ts'],
                        token=token,
                        as_user=as_user,
                    )
                    ok = res.body['ok']
                except APICallError as e:
                    ok = False
                    await report(bot, exception=e)
                if ok:
                    deletable = True
                    deleted += 1

    return deleted
