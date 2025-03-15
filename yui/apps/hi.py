import contextlib
import re

from ..box import box
from ..event import Message

HI_PATTERN_1 = re.compile(
    r"^(?:안녕(?:하세요)?|헬로우?|할로|하이|hello|hi)[!,?]*\s*(?:유이|yui)",
)
HI_PATTERN_2 = re.compile(
    r"^(?:유이|yui)\s*(?:안녕(?:하세요)?|헬로우?|할로|하이|hello|hi)[!,?]*",
)


@box.on(Message)
async def hi(bot, event: Message):
    if isinstance(event.text, str) and (
        HI_PATTERN_1.search(event.text.lower())
        or HI_PATTERN_2.search(event.text.lower())
    ):
        with contextlib.suppress(AttributeError):
            await bot.say(event.channel, f"안녕하세요! <@{event.user}>")
        return False
    return True
