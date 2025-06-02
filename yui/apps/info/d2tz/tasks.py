import asyncio
from typing import Final

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.expression import update

from ....bot import Bot
from ....box import box
from ....utils.datetime import fromtimestamp
from ....utils.datetime import now
from .commons import get_d2r_terror_zone_history
from .commons import get_d2r_terror_zone_info
from .commons import send_d2r_terror_zone_info_to_discord
from .models import TerrorZoneLog

DEFAULT_DELAY: Final = 60.0


async def on_start(bot: Bot):
    sess = bot.session_maker()

    now_dt = now()
    last_log: TerrorZoneLog | None = await sess.scalar(
        select(TerrorZoneLog).order_by(TerrorZoneLog.start_at.desc()).limit(1),
    )
    if last_log is None or last_log.start_at < now_dt:
        history = await get_d2r_terror_zone_history(
            bot.config.D2EMU_USERNAME,
            bot.config.D2EMU_TOKEN,
        )
        values = [
            {
                "levels": list(map(int, x["next"])),
                "start_at": fromtimestamp(x["next_terror_time_utc"]),
                "fetched_at": now_dt,
                "next_fetch_at": fromtimestamp(
                    max(
                        x["next_terror_time_utc"]
                        + x.get("delay", DEFAULT_DELAY),
                        x["next_available_time_utc"],
                    ),
                ),
            }
            for x in history
            if x["next"]
        ]
        await sess.execute(
            insert(TerrorZoneLog)
            .values(values)
            .on_conflict_do_nothing()
            .inline(),
        )
        await sess.commit()

    await sess.close()


async def broadcast(bot: Bot):
    sess = bot.session_maker()

    result = await sess.stream(
        select(TerrorZoneLog)
        .where(TerrorZoneLog.broadcasted_at.is_(None))
        .order_by(TerrorZoneLog.start_at.desc())
        .limit(12),
    )
    log: TerrorZoneLog
    output_slack = []
    output_discord = []
    min_id: int | None = None
    async for log in result.scalars():
        min_id = log.id if min_id is None else min(min_id, log.id)
        output_slack.append(log.to_slack_text())
        output_discord.append(log.to_discord_text())

    if min_id is not None:
        before_log: TerrorZoneLog = await sess.scalar(
            select(TerrorZoneLog)
            .where(TerrorZoneLog.id < min_id)
            .order_by(TerrorZoneLog.start_at.desc())
            .limit(1),
        )
        output_slack.append(before_log.to_slack_text())
        output_discord.append(before_log.to_discord_text())

    if output_slack:
        resp = await bot.say(
            bot.config.CHANNELS["d2r"],
            "\n".join(reversed(output_slack)),
        )
        if resp.is_ok():
            await sess.execute(
                update(TerrorZoneLog)
                .where(TerrorZoneLog.broadcasted_at.is_(None))
                .values(broadcasted_at=now()),
            )
            await sess.commit()

        discord_text = "\n".join(reversed(output_discord))
        for webhook_url in bot.config.DISCORD_WEBHOOKS["d2tz"]:
            await send_d2r_terror_zone_info_to_discord(
                webhook_url,
                discord_text,
            )

    await sess.close()


@box.polling_task()
async def polling_d2r_tz(bot: Bot):
    await on_start(bot)

    while True:
        sess = bot.session_maker()
        now_dt = now()
        last_log: TerrorZoneLog = await sess.scalar(
            select(TerrorZoneLog)
            .order_by(TerrorZoneLog.start_at.desc())
            .limit(1),
        )
        delta = max((last_log.next_fetch_at - now_dt).total_seconds(), 1.0)
        await sess.close()
        await asyncio.sleep(delta)

        data = await get_d2r_terror_zone_info(
            bot.config.D2EMU_USERNAME,
            bot.config.D2EMU_TOKEN,
        )
        if "ERROR" not in data and data["next"]:
            sess = bot.session_maker()
            await sess.execute(
                insert(TerrorZoneLog)
                .values(
                    levels=list(map(int, data["next"])),
                    start_at=fromtimestamp(data["next_terror_time_utc"]),
                    fetched_at=now_dt,
                    next_fetch_at=fromtimestamp(
                        max(
                            data["next_terror_time_utc"]
                            + data.get("delay", DEFAULT_DELAY),
                            data["next_available_time_utc"],
                        ),
                    ),
                )
                .on_conflict_do_nothing()
                .inline(),
            )
            await sess.commit()
            await sess.close()

            await broadcast(bot)

        else:
            await asyncio.sleep(DEFAULT_DELAY)
