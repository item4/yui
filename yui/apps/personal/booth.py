from typing import List, Optional, Tuple

import aiohttp

from lxml.html import fromstring

from sqlalchemy.orm.exc import NoResultFound

from ..shared.cache import JSONCache
from ...box import box
from ...command import C
from ...types.slack.attachment import Attachment, Field
from ...utils.api import retry
from ...utils.datetime import now

box.assert_channel_required('sao')

CATEGORY_TRANSLATE = {
    'Manga': '만화',
    'Illustration / CG collections': '일러스트북',
    'Illustrations': '일러스트',
    'Illustration (Other)': '일러스트',
    '4-panel Comics': '4컷만화',
}

BADGE_TRANSLATE = {
    'Adult': '성인물',
    '1 left in stock': '재고 1개 남음',
}


def get_or_create_cache(name: str, sess) -> JSONCache:
    try:
        cache = sess.query(JSONCache).filter_by(name=name).one()
    except NoResultFound:
        cache = JSONCache()
        cache.name = name
    return cache


def process(html: str, last_id: Optional[int]) -> Tuple[List[Attachment], int]:
    h = fromstring(html)
    items = h.cssselect('ul.items_basic li.item_basic')[::-1]
    attachments: List[Attachment] = []
    id = 0
    for item in items:
        id = int(item.get('data-product-id'))
        if last_id and id <= last_id:
            continue
        thumbnail_el = item.cssselect('a.thumbnail-image')[0]
        title_link = thumbnail_el.get('href')
        image_url = thumbnail_el.get('data-original')
        badges = [
            BADGE_TRANSLATE.get(x, x)
            for x in [
                el.text_content()
                for el in item.cssselect('.item-basic-badges .badge')
            ]
        ]
        events = [
            el.text_content()
            for el in item.cssselect(
                '.market-item-component__eventname-flags'
                ' .eventname-flag__name'
            )
        ]

        if '성인물' in badges:
            color = 'ff0000'
            image_url = None
        else:
            color = '3399ff'

        _category = item.cssselect('.item_summary-category')[0].text_content()
        category = CATEGORY_TRANSLATE.get(_category, _category)
        title = item.cssselect('.item_summary-title')[0].text_content()
        shop_el = item.cssselect('.item_summary-shop_name-field a.nav')[0]
        author_link = shop_el.get('href')
        author_name = shop_el.cssselect(
            'div.item_summary-shop_name')[0].text_content().strip()
        author_icon = shop_el.cssselect('img')[0].get('src')
        price = item.cssselect('.item_summary .price')[0].text_content()
        fields: List[Field] = [
            Field(
                title='카테고리',
                value=category,
                short=True,
            ),
            Field(
                title='가격',
                value=price,
                short=True,
            ),
        ]
        if badges:
            fields.append(Field(
                title='상태',
                value=' / '.join(badges),
                short=True,
            ))
        if events:
            fields.append(Field(
                title='관련 행사',
                value=' / '.join(events),
                short=True,
            ))
        attachments.append(Attachment(
            fallback=f'{title} - {title_link}',
            title=title,
            title_link=title_link,
            color=color,
            fields=fields,
            image_url=image_url,
            author_icon=author_icon,
            author_link=author_link,
            author_name=author_name,
        ))

    return attachments, id


@box.cron('0,20,40 * * * *')
async def watch(bot, sess):
    url = (
        'https://booth.pm/ko/search/'
        '%E3%82%BD%E3%83%BC%E3%83%89%E3%82%A2%E3%83%BC%E3%83%88%E3%83%BB'
        '%E3%82%AA%E3%83%B3%E3%83%A9%E3%82%A4%E3%83%B3?adult=include&'
        'floor=comic_illust&in_stock=true&sort=new'
    )
    headers = {
        'Cookie': 'adult=t',
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            html = await resp.text()

    cache = get_or_create_cache('personal-booth', sess)
    attachments, cache.body = await bot.run_in_other_process(
        process,
        html,
        cache.body,
    )

    if attachments:
        cache.created_at = now()
        with sess.begin():
            sess.add(cache)

        await retry(bot.api.chat.postMessage(
            channel=C.sao.get(),
            as_user=True,
            text='Booth에 소드 아트 온라인 신간이 올라왔어요!',
            attachments=attachments,
        ))
