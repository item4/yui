import re

from ..box import box
from ..event import Message

HASSAN_TRIGGER_RE = re.compile('^똑바로\s*서라\s*[,\.!]*\s*유이')


@box.command('안심')
async def relax(bot, event: Message):
    await bot.api.chat.postMessage(
        channel=event.channel,
        text='유이에게 나쁜 것을 주입하려는 사악한 재벌은 이 너굴맨이 처리했으니 안심하라구!',
        as_user=False,
        icon_url='https://i.imgur.com/dG6wXTX.jpg',
        username='너굴맨',
    )


@box.command('똥코드')
async def luwak(bot, event: Message):
    await bot.api.chat.postMessage(
        channel=event.channel,
        text='https://bucket.qdon.space/qdon/media_attachments/files/000/016/534/original/849158fb11372209.png',  # noqa
        as_user=False,
        icon_url='https://i.imgur.com/46eg1v9.jpg',
        username='지옥에서 온 램지'
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
