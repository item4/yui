from typing import Optional
from urllib.parse import quote

from lxml.html import fromstring

from ...api import Attachment
from ...bot import Bot
from ...box import box
from ...command import C
from ...event import Message
from ...session import client_session

box.assert_channel_required('general')

PACKTPUB_URL = 'https://www.packtpub.com/packt/offers/free-learning'


def parse_packtpub_dotd(html: str) -> Optional[Attachment]:
    h = fromstring(html)
    title_els = h.cssselect('.dotd-title')
    image_els = h.cssselect('.imagecache-dotd_main_image')
    if not title_els:
        return None
    title: str = title_els[0].text_content().strip()
    image_url = None
    if image_els:
        image_url = 'https://' + '/'.join(
            map(
                quote,
                image_els[0].get('src').replace('https://', '').split('/')
            )
        )
    return Attachment(
        fallback=f'{title} - {PACKTPUB_URL}',
        title=title,
        title_link=PACKTPUB_URL,
        text=f'오늘의 Packt Book Deal of The Day: {title} - {PACKTPUB_URL}',
        image_url=image_url,
    )


async def say_packtpub_dotd(bot: Bot, channel):
    async with client_session() as session:
        async with session.get(PACKTPUB_URL) as resp:
            html = await resp.text()

    attachment = await bot.run_in_other_process(
        parse_packtpub_dotd,
        html,
    )

    if attachment is None:
        await bot.say(
            channel,
            '오늘은 PACKT Book의 무료책이 없는 것 같아요'
        )
    else:
        await bot.api.chat.postMessage(
            channel=channel,
            text='오늘자 PACKT Book의 무료책이에요!',
            attachments=[attachment],
            as_user=True,
        )


@box.command('무료책', ['freebook'])
async def packtpub_dotd(bot, event: Message):
    """
    PACKT Book 무료책 안내

    PACKT Book에서 날마다 무료로 배부하는 Deal of The Day를 조회합니다.

    `{PREFIX}무료책` (오늘의 무료책)

    """

    await say_packtpub_dotd(bot, event.channel)


@box.crontab('5 9 * * *')
async def auto_packtpub_dotd(bot):
    await say_packtpub_dotd(bot, C.general.get())
