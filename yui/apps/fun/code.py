import random
import re
from datetime import timedelta

from ...box import box
from ...command.cooltime import Cooltime
from ...event import Message
from ...types.slack.attachment import Attachment

COOLTIME = timedelta(minutes=15)
PATTERN = re.compile(
    r"[제내저이]?\s*(?:코드|[PM]R|풀리퀘)좀?\s*리뷰",
)

ICON_URL = "https://i.imgur.com/bGVUlSp.jpg"
IMAGES = {
    "https://i.imgur.com/btkBRvc.png": 1,  # 루왁커피
    "https://i.imgur.com/v3bu01T.png": 1,  # 스파게티
    "https://i.imgur.com/UXyyFiM.png": 1,  # 갈아넣으면 된다더라
    "https://i.imgur.com/zDm1KBL.png": 1,  # 피클
    "https://i.imgur.com/XlYygAx.png": 0.3,  # Brilliant!
    "https://i.imgur.com/ODOVLQA.png": 0.5,  # 지사제
    "https://i.imgur.com/eu4SDBu.png": 0.5,  # DDLC Monika
}


async def write_code_review(bot, event: Message, *, seed=None):
    random.seed(seed)
    image_url = random.choices(*zip(*IMAGES.items(), strict=True))[0]
    random.seed(None)
    await bot.api.chat.postMessage(
        channel=event.channel,
        attachments=[Attachment(fallback=image_url, image_url=image_url)],
        icon_url=ICON_URL,
        username="코드램지",
    )


@box.on(Message)
async def code_review(bot, event: Message):
    if event.text and PATTERN.search(event.text.upper()):
        cooltime = Cooltime(
            bot=bot,
            key=f"YUI_APPS_FUN_CODE_REVIEW_{event.channel}",
            cooltime=COOLTIME,
        )
        if await cooltime.rejected() is None:
            await write_code_review(bot, event)
            await cooltime.record()
            return False
    return True
