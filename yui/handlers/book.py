from decimal import Decimal
from typing import List, Optional
from urllib.parse import quote

from lxml.html import fromstring

import ujson

from ..api import Attachment
from ..bot import Bot
from ..box import box
from ..command import C, argument
from ..event import Message
from ..session import client_session
from ..util import strip_tags

box.assert_config_required('NAVER_CLIENT_ID', str)
box.assert_config_required('NAVER_CLIENT_SECRET', str)
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


@box.command('책', ['book'])
@argument('keyword', nargs=-1, concat=True)
async def book(bot, event: Message, keyword: str):
    """
    책 검색

    책 제목으로 네이버 책 DB에서 검색합니다.

    `{PREFIX}책 소드 아트 온라인` (`소드 아트 온라인`으로 책 검색)

    """

    url = 'https://openapi.naver.com/v1/search/book.json'
    params = {
        'query': keyword,
    }
    headers = {
        'X-Naver-Client-Id': bot.config.NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': bot.config.NAVER_CLIENT_SECRET,
    }

    async with client_session() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            data = await resp.json(loads=ujson.loads)

    attachments: List[Attachment] = []

    count = min(5, len(data['items']))

    for i in range(count):
        book = data['items'][i]
        title = strip_tags(book['title'])
        attachments.append(Attachment(
            fallback='{} - {}'.format(title, book['link']),
            title=title,
            title_link=book['link'],
            thumb_url=book['image'],
            text='저자: {} / 출판사: {}{}'.format(
                strip_tags(book['author']),
                strip_tags(book['publisher']),
                ' / 정가: ￦{:,}'.format(Decimal(book['price']))
                if book['price'] else '',
            )
        ))

    if attachments:
        await bot.api.chat.postMessage(
            channel=event.channel,
            text=('키워드 *{}* (으)로 네이버 책 DB 검색 결과, 총 {:,}개의 결과가 나왔어요.'
                  ' 그 중 상위 {}개를 보여드릴게요!').format(
                keyword,
                data['total'],
                count,
            ),
            attachments=attachments,
            as_user=True,
            thread_ts=event.ts,
        )
    else:
        await bot.say(
            event.channel,
            '검색 결과가 없어요!'
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
            '오늘은 PACKT Book의 무료책이 없는데...다 읽었냐??'
        )
    else:
        await bot.api.chat.postMessage(
            channel=channel,
            text='오늘자 PACKT Book의 무료책이다...읽냐??',
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
