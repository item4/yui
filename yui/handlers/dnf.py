from typing import Any, Dict, List

import aiohttp

import ujson

from ..api import Attachment, Field
from ..box import box
from ..command import argument, option
from ..event import Message
from ..session import ClientSession
from ..transform import choice, value_range

RARITY_TABLE = {
    '커먼': '#FFFFFF',
    '언커먼': '68D5ED',
    '레어': 'B36BFF',
    '유니크': 'FF00FF',
    '레전더리': 'FF7800',
}


@box.command('던파경매장')
@option(
    '--word-type',
    default='front',
    transform_func=choice(['match', 'front', 'full'], fallback='front'),
)
@option(
    '--price-sort',
    default='asc',
    transform_func=choice(['asc', 'desc'], fallback='asc'),
)
@option(
    '--reinforce-sort',
    default='desc',
    transform_func=choice(['asc', 'desc'], fallback='desc'),
)
@option(
    '--limit',
    default=10,
    transform_func=value_range(1, 50, autofix=True),
)
@option('--min-level')
@option('--max-level')
@option('--min-reinforce')
@option('--max-reinforce')
@option('--min-refine')
@option('--max-refine')
@option('--rarity', transform_func=choice(list(RARITY_TABLE.keys())))
@argument('keyword', nargs=-1, concat=True)
async def dnf_auction(
    bot,
    event: Message,
    word_type: str,
    price_sort: str,
    reinforce_sort: str,
    limit: int,
    min_level: int,
    max_level: int,
    min_reinforce: int,
    max_reinforce: int,
    min_refine: int,
    max_refine: int,
    rarity: str,
    keyword: str,
):
    query = []
    if min_level is not None:
        query.append(f'minLevel:{min_level}')
    if max_level is not None:
        query.append(f'maxLevel:{max_level}')
    if min_reinforce is not None:
        query.append(f'minReinforce:{min_reinforce}')
    if max_reinforce is not None:
        query.append(f'maxReinforce:{max_reinforce}')
    if min_refine is None:
        query.append(f'minRefine:{min_refine}')
    if max_refine is not None:
        query.append(f'maxRefine:{max_refine}')
    if rarity is not None:
        query.append(f'rarity:{rarity}')

    params = {
        'itemName': keyword,
        'wordType': word_type,
        'sort': f'unitPrice:{price_sort},reinforce:{reinforce_sort}',
        'limit': limit,
        'apikey': bot.config.DNF_API_KEY,
    }
    if query:
        params['q'] = ','.join(query)
    data: Dict[str, Any] = {}
    try:
        async with ClientSession() as sess:
            async with sess.get(
                'https://api.neople.co.kr/df/auction',
                params=params
            ) as resp:
                data = await resp.json(loads=ujson.loads)
    except aiohttp.client_exceptions.ContentTypeError:
        await bot.say(
            event.channel,
            '던전 앤 파이터 API 서버 상태가 좋지 않아요! 나중에 시도해주세요!'
        )

    if data and data['rows']:
        attachments: List[Attachment] = []
        for row in data['rows']:
            title = '{} ({}/{}/{})'.format(
                row['itemName'],
                row['itemRarity'],
                row['itemType'],
                row['itemTypeDetail'],
            )
            fields: List[Field] = []
            if row['reinforce']:
                fields.append(Field('강화', f"+{row['reinforce']}", True))
            if row['refine']:
                fields.append(Field('제련', str(row['refine']), True))
            if row['amplificationName']:
                fields.append(Field('증폭', row['amplificationName'], True))
            fields.append(
                Field('즉시 구매 개당 가격', f"{row['unitPrice']:,}", True)
            )
            if row['averagePrice']:
                fields.append(
                    Field('평균 구매 가격', f"{row['averagePrice']:,}", True)
                )
            attachments.append(Attachment(
                fallback='{} - 즉구가 {:,} / 평균가 {:,}'.format(
                    title,
                    row['currentPrice'],
                    row['averagePrice'],
                ),
                title=title,
                fields=fields,
                thumb_url='https://img-api.neople.co.kr/df/items/{}'.format(
                    row['itemId'],
                ),
                color=RARITY_TABLE[row['itemRarity']],
            ))

        await bot.api.chat.postMessage(
            channel=event.channel,
            attachments=attachments,
            as_user=True,
            thread_ts=event.ts,
        )
    else:
        await bot.say(
            event.channel,
            '검색결과가 없어요!'
        )
