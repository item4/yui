import re

from ..box import box
from ..event import Message

HASSAN_TRIGGER_RE = re.compile('^똑바로\s*서라\s*[,\.!]*\s*유이')


@box.command('안심')
async def relax(bot, event: Message):
    await bot.api.chat.postMessage(
        channel=event.channel,
        text='https://pbs.twimg.com/profile_images/756486934747242496/Y0VaYlyr.jpg\r\n안심하십시오 괜찮습니다.',
        as_user=False,
        icon_url='https://i.imgur.com/GIHYPOx.jpg',
        username='우주안심수호자',
    )

@box.command('등심')
async def sirloin(bot, event: Message):
    await bot.api.chat.postMessage(
        channel=event.channel,
        text='https://i.imgur.com/ntil8cT.jpg',
        as_user=False,
        icon_url='https://i.imgur.com/X0pdPIM.jpg',
        username='고든렘지',
    )


@box.on(Message)
async def hassan(bot, event: Message):
    if HASSAN_TRIGGER_RE.search(event.text):
        try:
            await bot.say(
                event.channel,
                '저한테 왜 그러세요 @{}님?'.format(event.user.name)
            )
        except AttributeError:
            pass
        return False
    return True
