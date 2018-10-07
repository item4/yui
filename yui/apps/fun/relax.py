from ...box import box
from ...event import Message


@box.command('안심')
async def relax(bot, event: Message):
    """유이의 변절을 우려하는 분들을 위한 상태 점검 명령어"""

    await bot.api.chat.postMessage(
        channel=event.channel,
        text='유이에게 나쁜 것을 주입하려는 사악한 재벌은 이 너굴맨이 처리했으니 안심하라구!',
        as_user=False,
        icon_url='https://i.imgur.com/dG6wXTX.jpg',
        username='너굴맨',
    )
