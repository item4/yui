from ..box import box
from ..event import Message


@box.command('안심')
async def relax(bot, event: Message):
    await bot.api.chat.postMessage(
        channel=event.channel,
        text='유이에게 나쁜 것을 주입하려는 사악한 재벌은 이 너굴맨이 처리했으니 안심하라구!',
        as_user=False,
        icon_url='https://i.imgur.com/dG6wXTX.jpg',
        username='너굴맨',
    )


@box.on(Message)
async def hassan(bot, event: Message):
    if event.text.startswith('똑바로 서라 유이'):
        try:
            await bot.say(
                event.channel,
                '저한테 왜 그러세요 @{}님?'.format(event.user.name)
            )
        except AttributeError:
            pass
        return False
    return True
