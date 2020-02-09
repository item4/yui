from .models import EventLog
from ....box import box
from ....command import Cs
from ....event import Message


@box.on(Message, subtype='*')
async def make_log(bot, event: Message, sess):
    try:
        channels = Cs.auto_cleanup_targets.gets()
    except KeyError:
        return True

    if event.channel in channels:
        log = EventLog(channel=event.channel.id, ts=event.ts)
        with sess.begin():
            sess.add(log)
    return True
