from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.ext.asyncio import AsyncSession

from .models import EventLog
from ....box import box
from ....command import Cs
from ....event import Message


@box.on(Message, subtype='*')
async def make_log(bot, event: Message, sess: AsyncSession):
    try:
        channels = Cs.auto_cleanup_targets.gets()
    except KeyError:
        return True

    if event.subtype == 'message_deleted':
        return True

    if event.channel in channels:
        async with sess.begin_nested():
            await sess.execute(
                Insert(EventLog)
                .values(channel=event.channel.id, ts=event.ts)
                .on_conflict_do_nothing()
            )
    return True
