from decimal import Decimal
from typing import List

import aiohttp

import ujson

from ..api import Attachment
from ..box import box
from ..command import argument
from ..event import Message
from ..util import strip_tags


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

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            data = await resp.json(loads=ujson.loads)

    attachments: List[Attachment] = []

    count = min(3, len(data['items']))

    for i in range(count):
        book = data['items'][i]
        title = strip_tags(book['title'])
        attachments.append(Attachment(
            fallback='{} - {}'.format(title, book['link']),
            title=title,
            title_link=book['link'],
            thumb_url=book['image'],
            text='저자: {} / 출판사: {} / 정가: ￦{:,}'.format(
                strip_tags(book['author']),
                strip_tags(book['publisher']),
                Decimal(book['price']),
            )
        ))

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
    )
