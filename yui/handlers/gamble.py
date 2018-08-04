import random

from ..box import box
from ..command import option
from ..event import Message


DEALER_MESSAGE = [
    '힘껏 던진 결과입니다. {}입니다',
    '{}! 하하하',
    '{}',
    '유이가 기도하며 주사위를 굴려줬습니다. {}입니다.',
    '날아가던 주사위를 냥이가 쳐버렸네요. {}입니다.',
    '소라고둥님이 {}이랍니다.',
]


@box.command('dice', ['주사위'])
@option('--start', default=0)
@option('--end', default=100)
async def dice(bot, event: Message, start: int, end: int, seed: int=None):
    """
    주사위

    `{PREFIX}dice` (0부터 100사이의 수를 랜덤으로 출력)
    `{PREFIX}dice --start=1 --end=6` (1부터 6사이의 수를 랜덤으로 출력)

    """
    if start >= end:
        await bot.say(
            event.channel,
            '정상적인 범위를 입력해주세요!'
        )
        return

    random.seed(seed)

    number = random.randrange(start, end + 1)

    if number == 2:
        text = '콩'
    elif number == 22:
        text = '콩콩'
    else:
        text = random.choice(DEALER_MESSAGE).format(number)

    await bot.api.chat.postMessage(
        channel=event.channel,
        as_user=False,
        username='딜러',
        icon_url='https://i.imgur.com/8OcjS3o.jpg',
        text=text,
    )

    random.seed(None)
