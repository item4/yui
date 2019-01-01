import random
import re
from datetime import timedelta

from ...api import Attachment
from ...box import box
from ...event import Message
from ...utils.datetime import now

COOLTIME = timedelta(minutes=5)
PATTERN = re.compile(
    r'(?:고든|코드)?\s*램지님?\s*[제내저이]?\s*(?:코드|[PM]R|풀리퀘)좀?\s*리뷰',
)

ICON_URL = 'https://i.imgur.com/bGVUlSp.jpg'
IMAGES = {
    'https://i.imgur.com/btkBRvc.png': 2,  # 루왁커피
    'https://i.imgur.com/v3bu01T.png': 2,  # 스파게티
    'https://i.imgur.com/ODOVLQA.png': 1,  # 지사제
}


async def write_code_review(bot, event: Message, *, seed=None):
    random.seed(seed)
    image_url = random.choices(*zip(*IMAGES.items()))[0]
    random.seed(None)
    await bot.api.chat.postMessage(
        channel=event.channel,
        attachments=[
            Attachment(
                fallback=image_url,
                image_url=image_url,
            ),
        ],
        as_user=False,
        icon_url=ICON_URL,
        username='코드램지',
    )


@box.on(Message)
async def code_review(bot, event: Message):
    if PATTERN.search(event.text.upper()):
        now_dt = now()
        last_call = code_review.last_call.get(event.channel.id)
        cond = last_call is None
        if not cond:
            cond = last_call + COOLTIME <= now_dt

        if cond:
            await write_code_review(bot, event)
            code_review.last_call[event.channel.id] = now_dt
            return False
    return True
