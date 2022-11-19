from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ....box import box
from ....event import Message
from .models import EventLog


@box.on(Message, subtype="*")
async def make_log(bot, event: Message, sess: AsyncSession):
    try:
        channels = bot.config.CHANNELS["auto_cleanup_targets"]
    except KeyError:
        return True

    if event.subtype == "message_deleted":
        return True

    if event.channel in channels:
        await sess.execute(
            insert(EventLog)
            .values(channel=event.channel, ts=event.ts)
            .on_conflict_do_nothing()
        )
        await sess.commit()
    return True
