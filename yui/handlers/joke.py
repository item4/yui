import re

from ..api import Attachment
from ..box import box
from ..event import Message

HASSAN_TRIGGER_RE = re.compile('^똑바로\s*서라\s*[,\.!]*\s*유이')


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


@box.command('똥코드')
async def luwak(bot, event: Message):
    """공짜 코드 리뷰"""

    await bot.api.chat.postMessage(
        channel=event.channel,
        attachments=[
            Attachment(
                fallback='니 코드가 너무 똥같아서 루왁커피를 만들 수도 있겠다!',
                image_url='https://bucket.qdon.space/qdon/media_attachments/'
                          'files/000/016/534/original/849158fb11372209.png'
            ),
        ],
        as_user=False,
        icon_url='https://i.imgur.com/46eg1v9.jpg',
        username='지옥에서 온 램지'
    )


@box.command('gdpr')
async def gdpr(bot, event: Message):
    """
    Privacy policy update
    """
    await bot.api.chat.postMessage(
        channel=event.channel,
        attachments=[
            Attachment(
                fallback='Wake up gordon',
                image_url='https://files.mastodon.social/media_attachments'
                '/files/004/192/196/original/f19cfcbb0830aafa.png'
            ),
            Attachment(
                fallback='We have updated our privacy policy',
                image_url='https://files.mastodon.social/media_attachments'
                '/files/004/192/197/original/bead89e8ae197ecd.png'
            ),
        ],
        as_user=False,
        icon_url='https://pm1.narvii.com/6046/'
        'dcf537e42d788e13cd2f51da1f6d60d277e554f4_128.jpg',
        username='G-man'
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
