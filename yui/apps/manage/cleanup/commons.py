import asyncio
import random
from typing import Optional

from .models import EventLog
from ....bot import APICallError
from ....types.channel import Channel


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
        resp = await bot.api.chat.delete(
            log.channel,
            log.ts,
            token=bot.config.OWNER_USER_TOKEN,
        )
        ok = resp.body['ok']
        if ok or (not ok and resp.body['error'] == 'message_not_found'):
            deleted += ok
            with sess.begin():
                sess.delete(log)
        await asyncio.sleep(random.uniform(0.02, 0.5))

    return deleted


async def cleanup_by_history(
    bot,
    channel: Channel,
    ts: str,
    token: Optional[str],
    count: int = 100,
    as_user: bool = False,
) -> int:
    deleted = 0
    deletable = True
    while deletable and deleted < count:
        history = await bot.api.conversations.history(
            channel,
            count=count,
            latest=ts,
            unreads=True,
        )
        deletable = False
        if history.body['ok']:
            for message in history.body['messages']:
                try:
                    r = await bot.api.chat.delete(
                        channel,
                        message['ts'],
                        token=token,
                        as_user=as_user,
                    )
                    ok = r.body['ok']
                except APICallError:
                    ok = False
                if ok:
                    deletable = True
                    deleted += 1

                await asyncio.sleep(random.uniform(0.02, 0.5))
            await asyncio.sleep(random.uniform(1.0, 3.0))

    return deleted
