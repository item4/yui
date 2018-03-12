import random
from typing import List

from ..box import box
from ..event import Message

RESPONSES: List[str] = [
    '그래',
    '돼',
    '안돼',
    '기다려',
    '맘대로 해',
    '당장 시작해',
    '지금이야',
    '몰라',
    '안들려',
    '같이가',
    '너만 가',
    '뭐',
    '맞아',
    '아닌데',
    '^^...',
    'ㅇㅇ',
    'ㄴㄴ',
    '어쩌라고',
    '후...',
    '빠잉',
    '반가워',
    '잘가',
    '하이',
    '공부하자',
    '웅?',
    '어',
    '포기해',
    '포기하지마',
    'ㄱㄱ',
    '아아안 돼애에',
    '나중에 해',
    '지금 해',
    '허락할게',
    '허락 못 해',
    '둘 다 하지 마',
    '둘 다 해',
    '응',
    '아니',
    '다시 한번 물어봐',
    '가만히 있어',
    '도망가',
    '해',
    '하지마',
]
icon_url = 'https://i.imgur.com/uDcouRb.jpg'


@box.on(Message)
async def magic_conch(bot, event: Message):
    if event.text.startswith('마법의 소라고둥님'):
        await bot.api.chat.postMessage(
            channel=event.channel,
            text=random.choice(RESPONSES),
            as_user=False,
            icon_url=icon_url,
            username='마법의 소라고둥',
        )
        return False
    return True
