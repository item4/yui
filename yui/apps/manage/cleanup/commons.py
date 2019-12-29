import asyncio
from typing import Optional


from .models import EventLog
from ....types.channel import Channel


async def cleanup_by_event_logs(
    bot,
    sess,
    channel: Channel,
    ts: str,
    count: Optional[int] = None,
) -> int:
    deleted = 0
    logs = sess.query(EventLog).filter(
        EventLog.channel == channel.id,
        EventLog.ts <= ts,
    ).order_by(EventLog.ts.desc())
    if count:
        logs = logs.limit(count)
    for log in logs:  # type: EventLog
        resp = await bot.api.chat.delete(
            log.channel,
            log.ts,
            token=bot.config.OWNER_USER_TOKEN,
        )
        ok = resp.body['ok']
        if ok or (
            not ok
            and resp.body['error'] == 'message_not_found'
        ):
            deleted += ok
            with sess.begin():
                sess.delete(log)
        await asyncio.sleep(0.02)

    return deleted


async def cleanup_by_history(
    bot,
    channel: Channel,
    ts: str,
    count: int = 100,
) -> int:
    deleted = 0
    history = await bot.api.channels.history(
        channel,
        count=count,
        latest=ts,
        unreads=True,
    )

    if history.body['ok']:
        for message in history.body['messages']:
            r = await bot.api.chat.delete(
                channel,
                message['ts'],
                token=bot.config.OWNER_USER_TOKEN,
            )
            if not r.body['ok']:
                break
            deleted += 1
            await asyncio.sleep(0.1)

    return deleted
