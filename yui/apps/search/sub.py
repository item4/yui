import asyncio
import math
import urllib.parse
from datetime import datetime
from typing import Any, Dict, List, NamedTuple

import aiohttp

import async_timeout

from fuzzywuzzy import fuzz

import ujson

from ...api import Attachment
from ...box import box
from ...command import argument, option
from ...event import Message
from ...session import client_session
from ...util import fuzzy_korean_partial_ratio


class Sub(NamedTuple):

    maker: str
    episode_num: float
    url: str
    released_at: str


DOW = [
    '일요일',
    '월요일',
    '화요일',
    '수요일',
    '목요일',
    '금요일',
    '토요일',
    '기타',
]
DATE_FORMAT = '%Y년 %m월 %d일 %H시'


def print_time(t: str) -> str:
    return '{}:{}'.format(t[:2], t[2:])


def encode_url(u: str) -> str:
    prefix = ''
    if u.startswith('http://'):
        prefix = 'http://'
    elif u.startswith('https://'):
        prefix = 'https://'
    u = u[len(prefix):]
    return prefix + '/'.join(urllib.parse.quote(c) for c in u.split('/'))


def fix_url(url: str) -> str:
    if url.startswith('https://') or url.startswith('http://'):
        return url
    return 'http://{}'.format(url)


def make_sub_list(data: List[Sub]) -> List[Attachment]:
    result: List[Attachment] = []

    if data:
        for sub in data:
            num = '완결' if sub.episode_num == 9999 else f'{sub.episode_num}화'
            name = sub.maker
            url = fix_url(sub.url)
            released_at = None
            try:
                released_at = datetime.strptime(
                    sub.released_at,
                    '%Y%m%d%H%M%S',
                )
            except ValueError:
                pass
            if released_at:
                date = released_at.strftime(DATE_FORMAT)
                fallback = f'{num} {date} {name} {url}'
                text = f'{num} {date} {url}'
            else:
                fallback = f'{num} {name} {url}'
                text = f'{num} {url}'
            result.append(
                Attachment(
                    fallback=fallback,
                    author_name=name,
                    text=text,
                )
            )
    else:
        result.append(
            Attachment(
                fallback='자막 제작자가 없습니다.',
                text='자막 제작자가 없습니다.',
            )
        )

    return result


async def get_json(*args, timeout: float=0.5, **kwargs):
    weight = 1
    while True:
        async with async_timeout.timeout(timeout):
            async with client_session() as session:
                try:
                    async with session.get(*args, **kwargs) as res:
                        if res.status != 200:
                            return []
                        try:
                            return await res.json(loads=ujson.loads)
                        except aiohttp.client_exceptions.ClientResponseError:
                            return ujson.loads(await res.text())
                except aiohttp.client_exceptions.ServerDisconnectedError:
                    if weight > 10:
                        raise
                    else:
                        await asyncio.sleep(weight/10)
                        weight += 1
                except ValueError:
                    return []


async def get_weekly_list(url, week, timeout: float=0.5):
    weight = 1
    while True:
        res = await get_json('{}?w={}'.format(url, week), timeout=timeout)
        if res:
            for r in res:
                r['week'] = week
            return res
        await asyncio.sleep(weight/10)
        weight += 1


@box.command('sub', ['애니자막'])
@option('--finished/--on-air', '--종영/--방영', '--완결/--방송', '--fin/--on',
        '-f/-o')
@argument('title', nargs=-1, concat=True, count_error='애니 제목을 입력해주세요')
async def sub(bot, event: Message, finished: bool, title: str):
    """
    애니메이션 자막을 검색합니다

    OHLI와 애니시아 자막 편성표에서 주어진 제목과 가장 근접한 제목의 애니를 검색하여 보여줍니다.

    방영중 애니 검색은 기본적으로 OHLI의 자막 목록에서 fuzzy search 후, OHLI에서 제공하는
    ALIAS를 기준으로 삼아 애니시아의 자막 목록에서 검색합니다. 따라서 OHLI와 애니시아의 애니명이
    다른 경우에는 검색이 가능하지만, OHLI에 아예 없는 애니는 검색이 불가능합니다.

    종영 애니 포함 검색은 OHLI만을 검색합니다. OHLI의 검색 API를 이용하기 때문에
    fuzzy search를 지원하지 않습니다.

    `{PREFIX}sub 이나즈마 일레븐` (제목이 `'이나즈마 일레븐'` 에 근접하는 것을 검색)
    `{PREFIX}sub 나 히 아` (제목이 `'나 히 아'` 에 근접하는 것을 검색)
    `{PREFIX}sub 히로아카` (OHLI의 애니 별칭 목록에 있는것은 별칭으로도 검색 가능)
    `{PREFIX}sub --완결 aldnoah` (제목에 `'aldnoah'`가 들어가는 애니 + 완결애니를 검색)

    """

    if finished:
        await search_finished(bot, event, title)
    else:
        await search_on_air(bot, event, title)


async def search_on_air(bot, event: Message, title: str, timeout: float=0.5):

    ohli = []
    anissia = []
    for w in range(7+1):
        ohli.append(
            get_weekly_list('http://ohli.moe/anitime/list', w, timeout)
        )
        anissia.append(
            get_weekly_list('http://www.anissia.net/anitime/list', w, timeout)
        )

    o_responses, _ = await asyncio.wait(
        ohli,
        return_when=asyncio.FIRST_EXCEPTION,
    )
    a_responses, _ = await asyncio.wait(
        anissia,
        return_when=asyncio.FIRST_EXCEPTION,
    )
    o_data: List[Dict[str, Any]] = []
    a_data: List[Dict[str, Any]] = []

    for response in o_responses:
        try:
            res = response.result()
        except Exception as e:
            await bot.say(
                event.channel,
                'Error: {}: {}'.format(e.__class__.__name__, e)
            )
            return
        else:
            o_data.extend(res)
    for r in a_responses:
        try:
            res = r.result()
        except Exception:
            a_data.clear()
            break
        else:
            a_data.extend(res)

    for ani in o_data:
        ani['ratio'] = max(
            fuzzy_korean_partial_ratio(
                title.lower(),
                a['s'].lower(),
            ) for a in ani['n']
        )

    o_ani = max(o_data, key=lambda x: x['ratio'])

    if o_ani['ratio'] > 10:
        result: List[Sub] = []

        o_subs = await get_json(
            'http://ohli.moe/cap/{}'.format(o_ani['i'])
        )

        for sub in o_subs:
            episode_num = sub['s']
            if int(math.ceil(episode_num)) == int(episode_num):
                episode_num = int(episode_num)
            result.append(Sub(
                maker=sub['n'],
                episode_num=episode_num,
                url=sub['a'],
                released_at=sub['d'],
            ))

        use_anissia = False
        a_ani = None
        if a_data:
            for ani in a_data:
                ani['ratio'] = max(
                    fuzzy_korean_partial_ratio(
                        alias['s'].lower(),
                        ani['s'].lower()
                    ) for alias in o_ani['n']
                )

                if o_ani['t'] == ani['t']:
                    ani['ratio'] += 5
                if o_ani['week'] == ani['week']:
                    ani['ratio'] += 5
                if fuzz.ratio(fix_url(ani['l']), o_ani['l']) > 94:
                    ani['ratio'] += 10

            a_ani = max(a_data, key=lambda x: x['ratio'])

            if a_ani['ratio'] > 80:
                use_anissia = True

                a_subs = await get_json(
                    'http://www.anissia.net/anitime/cap?i={}'.format(
                        a_ani['i']
                    )
                )

                for sub in a_subs:
                    url = fix_url(encode_url(sub['a']))
                    if o_subs and max(
                        fuzz.ratio(url.lower(), o_sub['a'].lower())
                        for o_sub in o_subs
                    ) > 95:
                        continue
                    episode_num = int(sub['s'])/10
                    if int(math.ceil(episode_num)) == int(episode_num):
                        episode_num = int(episode_num)
                    result.append(Sub(
                        maker=sub['n'],
                        episode_num=episode_num,
                        url=url,
                        released_at=sub['d'],
                    ))

        title = o_ani['s']
        dow = DOW[o_ani['week']]
        time = print_time(o_ani['t'])
        url = fix_url(o_ani['l'])
        if use_anissia and a_ani:
            pretext = (
                '애니시아와 OHLI의 자막 DB에서 요청하신것과 가장 비슷한 제목의 애니메이션을 '
                '찾았어요! 양측의 DB의 내용을 종합해서 알려드릴게요!'
            )
            genre = a_ani['g'].replace(' ', '')
            fallback = f'*{title}* ({dow} {time} / {genre} / {url})'
            text = f'{dow} {time} / {genre}'
        else:
            pretext = (
                'OHLI의 자막 DB에서 요청하신것과 가장 비슷한 제목의 애니메이션을 '
                '찾았어요! 아쉽지만 애니시아에선 찾지 못했어요. OHLI DB의 내용을 알려드릴게요!'
            )
            fallback = f'*{title}* ({dow} {time} / {url})'
            text = f'{dow} {time}'

        attachments: List[Attachment] = [
            Attachment(
                fallback=fallback,
                title=title,
                title_link=url,
                text=text,
                thumb_url=o_ani['img'] or None,
                pretext=pretext,
            ),
        ]
        attachments.extend(make_sub_list(result))

        await bot.api.chat.postMessage(
            channel=event.channel,
            attachments=attachments,
            as_user=True,
            thread_ts=event.ts,
        )

    else:
        await bot.say(
            event.channel,
            '해당 제목의 애니는 찾을 수 없어요!'
        )


async def search_finished(bot, event: Message, title: str):

    data = await get_json(
        'http://ohli.moe/timetable/search?{}'.format(
            urllib.parse.urlencode({'query': title.encode()})
        )
    )

    if data:
        chat = await bot.say(
            event.channel,
            (
                f'완결애니를 포함하여 OHLI DB에서 검색한 결과 총 {len(data):,}개의'
                ' 애니가 검색되었어요!\n검색 결과는 도배의 우려가 있어서 thread로 남길게요!'
            )
        )
        ts = chat['ts'] if chat['ok'] else event.event_ts
        for ani in data:
            subs = await get_json(
                'http://ohli.moe/cap/{}'.format(ani['i']))
            result: List[Sub] = []

            for sub in subs:
                episode_num = sub['s']
                if int(math.ceil(episode_num)) == int(episode_num):
                    episode_num = int(episode_num)
                result.append(Sub(
                    maker=sub['n'],
                    episode_num=episode_num,
                    url=sub['a'],
                    released_at=sub['d'],
                ))

            attachments: List[Attachment] = [
                Attachment(
                    fallback='*{title}* ({url})'.format(
                        title=ani['s'],
                        url=fix_url(ani['l']),
                    ),
                    title=ani['s'],
                    title_link=fix_url(ani['l']) if ani['l'] else None,
                    thumb_url=ani['img'] or None,
                ),
            ]
            attachments.extend(make_sub_list(result))

            await bot.api.chat.postMessage(
                channel=event.channel,
                attachments=attachments,
                as_user=True,
                thread_ts=ts,
            )
    else:
        await bot.say(
            event.channel,
            '해당 제목의 완결 애니는 찾을 수 없어요!',
        )
