from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import delete
from sqlalchemy.sql.expression import select

from ....bot import APICallError
from ....types.base import ChannelID
from ....utils.report import report
from .models import EventLog


async def cleanup_by_event_logs(
    bot,
    sess: AsyncSession,
    channel_id: ChannelID,
    ts: str,
    token: str | None,
    count: int | None = None,
) -> int:
    stmt = (
        select(EventLog)
        .where(
            EventLog.channel == channel_id,
            EventLog.ts <= ts,
        )
        .order_by(EventLog.ts.desc())
    )

    if count:
        stmt = stmt.limit(count)

    result = await sess.stream(stmt)

    deleted: set[int] = set()

    log: EventLog
    async for log in result.scalars():
        try:
            resp = await bot.api.chat.delete(
                log.channel,
                log.ts,
                token=token,
            )
        except APICallError as e:
            await report(bot, exception=e)
            return len(deleted)
        ok = resp.body["ok"]
        if ok or (not ok and resp.body["error"] == "message_not_found"):
            deleted.add(log.id)

    if deleted:
        await sess.execute(
            delete(EventLog).where(EventLog.id.in_(list(deleted))),
        )
        await sess.commit()

    return len(deleted)


async def cleanup_by_history(
    bot,
    sess: AsyncSession,
    channel_id: ChannelID,
    ts: str,
    token: str | None,
    minimum: int = 100,
) -> int:
    deleted = 0
    deletable = True
    while deletable and deleted < minimum:
        try:
            resp = await bot.api.conversations.history(
                channel_id,
                latest=ts,
            )
        except APICallError as e:
            await report(bot, exception=e)
            break
        history = resp.body
        deletable = False
        if history["ok"]:
            messages = simplify_history_result(history["messages"])
            while messages:
                message = messages.pop(0)
                reply_count = message["reply_count"]
                if reply_count:
                    try:
                        r = await bot.api.conversations.replies(
                            channel_id,
                            ts=message["ts"],
                        )
                    except APICallError as e:
                        await report(bot, exception=e)
                        break
                    messages += simplify_history_result(
                        r.body.get("messages", [])[1:],
                    )
                try:
                    res = await bot.api.chat.delete(
                        channel_id,
                        message["ts"],
                        token=token,
                    )
                    ok = res.body["ok"]
                except APICallError as e:
                    ok = False
                    await report(bot, exception=e)
                if ok:
                    deletable = True
                    deleted += 1
                    await sess.execute(
                        delete(EventLog).where(
                            EventLog.channel == channel_id,
                            EventLog.ts == message["ts"],
                        ),
                    )
                    await sess.commit()

    return deleted


async def collect_history_from_channel(
    bot,
    channel_id: ChannelID,
    sess: AsyncSession,
) -> int:
    cursor = None
    collected: set[tuple[str, str]] = set()
    try:
        while True:
            try:
                resp = await bot.api.conversations.history(
                    channel_id,
                    cursor=cursor,
                )
            except APICallError as e:
                await report(bot, exception=e)
                raise RuntimeError from e

            history = resp.body
            if not history["ok"]:
                await report(
                    bot,
                    exception=APICallError(
                        method="conversations.history",
                        headers={},
                        data=history,
                    ),
                )
                raise RuntimeError

            cursor = (
                history["response_metadata"]["next_cursor"]
                if "response_metadata" in history
                else None
            )

            messages = simplify_history_result(history["messages"])
            while messages:
                message = messages.pop(0)
                reply_count = message["reply_count"]
                if reply_count:
                    try:
                        r = await bot.api.conversations.replies(
                            channel_id,
                            ts=message["ts"],
                        )
                    except APICallError as e:
                        await report(bot, exception=e)
                    else:
                        messages += simplify_history_result(
                            r.body.get("messages", [])[1:],
                        )
                collected.add((channel_id, message["ts"]))
            if cursor is None:
                break
    finally:
        if collected:
            await sess.execute(
                insert(EventLog)
                .values([{"channel": cid, "ts": ts} for cid, ts in collected])
                .on_conflict_do_nothing()
                .inline(),
            )
            await sess.commit()
    return len(collected)


def simplify_history_result(rows: list[dict]) -> list[dict]:
    return [
        {
            "ts": row["ts"],
            "reply_count": row.get("reply_count", 0),
        }
        for row in rows
    ]
