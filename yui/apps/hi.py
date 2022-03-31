import re

from ..box import box
from ..event import Message

HI_RE1 = re.compile(
    r"^(?:안녕(?:하세요)?|헬로우?|할로|하이|hello|hi)[!,\?]*\s*유이",
    re.IGNORECASE,
)
HI_RE2 = re.compile(
    r"^유이\s*(?:안녕(?:하세요)?|헬로우?|할로|하이|hello|hi)[!,\?]*",
    re.IGNORECASE,
)


@box.on(Message)
async def hi(bot, event: Message):
    if HI_RE1.search(event.text) or HI_RE2.search(event.text):
        try:
            await bot.say(event.channel, "안녕하세요! <@{}>".format(event.user))
        except AttributeError:
            pass
        return False
    return True
