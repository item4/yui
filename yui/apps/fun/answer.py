import random
import re

from ...box import box
from ...event import Message

RESPONSES: list[str] = [
    "그래",
    "그럴걸?",
    "돼",
    "될걸?",
    "안돼",
    "안될걸?",
    "기다려",
    "존버해",
    "맘대로 해",
    "당장 시작해",
    "지금이야",
    "몰라",
    "ㅁㄹ",
    "안들려",
    "같이가",
    "좋은건 나도",
    "너만 가",
    "혼자 가",
    "뭐",
    "뭐?",
    "맞아",
    "마즘",
    "아닌데",
    "아닌디",
    "^^...",
    "ㅎㅎ...",
    "ㅇㅇ",
    "ㅇㅇㅇㅇㅇㅇㅇ",
    "ㄴㄴ",
    "ㄴㄴㄴㄴㄴㄴㄴ",
    "어쩌라고",
    "어쩔",
    "후...",
    "하...",
    "빠잉",
    "ㅃㅃ",
    "반가워",
    "하잉",
    "잘가",
    "하이",
    "헬로",
    "공부하자",
    "생각좀 하자",
    "웅?",
    "우웅?",
    "난 그런거 몰라여",
    "어",
    "포기해",
    "손절 ㄱ",
    "포기하지마",
    "손절 ㄴ",
    "ㄱㄱ",
    "ㄱㄱㄱㄱㄱㄱ",
    "가즈아",
    "아아안 돼애에",
    "나중에 해",
    "지금 해",
    "허락할게",
    "허락 못 해",
    "모두 하지 마",
    "모두다 해",
    "응",
    "아니",
    "다시 한번 물어봐",
    "가만히 있어",
    "도망가",
    "해",
    "하지마",
    "ㅋㅋㅋ",
    "ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ",
    "ㅠㅠ",
    "ㅠㅠㅠㅠㅠㅠㅠ",
    "ㅋㅋㅋㅋㅋㅋ큐ㅠㅠㅠㅠㅠㅠ",
]
icon_url = "https://i.imgur.com/uDcouRb.jpg"

SUMMON_PREFIX = re.compile(r"^마법의?\s*소라고[둥동]님?\s*")


@box.on(Message)
async def magic_conch(bot, event: Message):
    if event.text and SUMMON_PREFIX.search(event.text):
        await bot.api.chat.postMessage(
            channel=event.channel,
            text=random.choice(RESPONSES),
            icon_url=icon_url,
            username="마법의 소라고둥",
        )
        return False
    return True
