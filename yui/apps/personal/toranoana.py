import asyncio
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import attr

from lxml.html import fromstring

from sqlalchemy.orm.exc import NoResultFound

from ..shared.cache import JSONCache
from ...box import box
from ...command import C
from ...session import client_session
from ...types.slack.attachment import Attachment, Field
from ...utils.api import retry
from ...utils.datetime import now


@attr.dataclass()
class Page:

    url: str
    genre: str
    target: str
    restrict: str

    @property
    def label(self) -> str:
        return f'{self.genre} {self.target} {self.restrict}'

    @property
    def base_url(self) -> str:
        u = urlparse(self.url)
        return f'{u.scheme}://{u.hostname}'


def get_or_create_cache(name: str, sess) -> JSONCache:
    try:
        cache = sess.query(JSONCache).filter_by(name=name).one()
    except NoResultFound:
        cache = JSONCache()
        cache.name = name
    return cache


def process(
    html: str,
    page: Page,
    cache: Optional[List[str]],
) -> Tuple[List[Attachment], List[str]]:
    h = fromstring(html)
    items = h.cssselect('#search-result-container li.list__item')[::-1]
    attachments: List[Attachment] = []
    if cache is None:
        cache = []
    current = []
    for item in items:
        id = item.cssselect('input#commodityCode')[0].get('value').strip()
        current.append(id)
        if id in cache:
            continue
        thumbnail_container = item.cssselect('.product_img a')[0]
        image_url = thumbnail_container[-1].get('data-src').strip()
        title_link = (
            page.base_url +
            thumbnail_container.get('href').strip()
        )
        title = item.cssselect('.product_title')[0].text_content().strip()
        labels_els = item.cssselect('.product_labels')
        remain = labels_els[1][0].text_content().strip()[0]
        author_name = ', '.join(
            el.text_content().strip() for el in labels_els[0][0]
        )
        circle_name = ', '.join(
            el.text_content().strip() for el in labels_els[0][1]
        )
        price = item.cssselect('.product_price')[0].text_content().strip()
        if any(
            '18禁' in li.text_content().strip()
            for li in item.cssselect('.product_tags li')
        ):
            color = 'ff0000'
        else:
            color = '3399ff'

        fields: List[Field] = [
            Field(
                title='장르',
                value=page.genre,
                short=True,
            ),
            Field(
                title='타겟',
                value=page.target,
                short=True,
            ),
            Field(
                title='가격',
                value=price,
                short=True,
            ),
            Field(
                title='재고',
                value=remain,
                short=True,
            ),
        ]
        attachments.append(Attachment(
            fallback=f'{title} - {title_link}',
            title=title,
            title_link=title_link,
            color=color,
            fields=fields,
            image_url=image_url,
            author_name=f'{author_name} ({circle_name})',
        ))

    return attachments, current


@box.cron('0,30 * * * *')
async def watch(bot, sess):
    pages: List[Page] = [
        Page(
            url=('https://ec.toranoana.shop/'
                 'tora/ec/cot/genre/GNRN00001186/all/all/'),
            genre='소드 아트 온라인',
            target='남성향',
            restrict='전연령',
        ),
        Page(
            url=('https://ec.toranoana.shop/'
                 'joshi/ec/cot/genre/GNRN00001186/all/all/'),
            genre='소드 아트 온라인',
            target='여성향',
            restrict='전연령',
        ),
        Page(
            url=('https://ec.toranoana.jp/'
                 'joshi_r/ec/cot/genre/GNRN00001186/all/all/'),
            genre='소드 아트 온라인',
            target='여성향',
            restrict='성인',
        ),
        Page(
            url=('https://ec.toranoana.shop/'
                 'joshi/ec/cot/genre/GNRN00003507/all/all/'),
            genre='아이돌마스터 SideM',
            target='여성향',
            restrict='전연령',
        ),
        Page(
            url=('https://ec.toranoana.jp/'
                 'joshi_r/ec/cot/genre/GNRN00003507/all/all/'),
            genre='아이돌마스터 SideM',
            target='여성향',
            restrict='성인',
        ),
    ]
    headers = {
        'Cookie': 'adflg=0',
    }

    for page in pages:
        async with client_session() as session:
            async with session.get(page.url, headers=headers) as resp:
                html = await resp.text()

        cache = get_or_create_cache(page.label, sess)
        attachments, cache.body = await bot.run_in_other_process(
            process,
            html,
            page,
            cache.body,
        )

        if attachments:
            cache.created_at = now()
            with sess.begin():
                sess.add(cache)

            await retry(bot.api.chat.postMessage(
                channel=C.toranoana.get(),
                as_user=True,
                text=f'토라노아나 {page.genre} 신간을 안내드릴게요!',
                attachments=attachments,
            ))

        await asyncio.sleep(2*60)
