import re

from ...box import box
from ...event import Message

HASSAN_TRIGGER_PATTERN = re.compile(r'^똑바로\s*서라\s*[,\.!]*\s*유이')


@box.on(Message)
async def hassan(bot, event: Message):
    if HASSAN_TRIGGER_PATTERN.search(event.text):
        try:
            await bot.say(
                event.channel,
                '저한테 왜 그러세요 @{}님?'.format(event.user.name)
            )
        except AttributeError:
            pass
        return False
    return True
