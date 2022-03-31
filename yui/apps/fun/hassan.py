import re

from ...box import box
from ...event import Message
from ...utils import format

HASSAN_TRIGGER_PATTERN = re.compile(r"^똑바로\s*서라\s*[,\.!]*\s*유이")


@box.on(Message)
async def hassan(bot, event: Message):
    if HASSAN_TRIGGER_PATTERN.search(event.text):
        await bot.say(
            event.channel,
            f"저한테 왜 그러세요 {format.link(event.user)}님?",
        )
        return False
    return True
