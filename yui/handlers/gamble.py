import random
import functools

from ..box import box
from ..event import Message

@box.command('dice', ['주사위'])
async def dice(bot, event: Message):
    number = random.randrange(0,100)

    if number == 2:
        text = '콩'
    elif number == 22: 
        text = '콩콩'
    else: 
        text = random.choice(['힘껏 던진 결과입니다. {}입니다','{}! 하하하','{}','유이가 기도하며 주사위를 굴려줬습니다. {}입니다.','날아가던 주사위를 냥이가 쳐버렸네요. {}입니다.','소라고둥님이 {}이랍니다.'])
        text = text.format(number)

    await bot.api.chat.postMessage(
        channel=event.channel,
        as_user=False,
        username='딜러',
        icon_url='https://i.imgur.com/8OcjS3o.jpg',
        text = text
    )
