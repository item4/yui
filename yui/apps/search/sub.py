import asyncio
import math
import urllib.parse
from datetime import datetime
from typing import Any

import aiohttp
import aiohttp.client_exceptions

import async_timeout

import attr

from fuzzywuzzy import fuzz

from ...box import box
from ...command import argument
from ...command import option
from ...event import Message
from ...types.slack.attachment import Attachment
from ...utils import json
from ...utils.fuzz import match


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


def fix_url(url: str) -> str:
    if 'blog.naver.com' in url or '.tistory.com' in url or '.blog.me' in url:
        if url.startswith('http'):
            url = url.split('//', 1)[1]
        return f'https://{url}'
    elif url.startswith('http://') or url.startswith('https://'):
        return url
    return f'http://{url}'


def convert_released_dt(input: str) -> str:
    try:
        return datetime.strptime(input, '%Y%m%d%H%M%S').strftime(DATE_FORMAT)
    except ValueError:
        return str(input)


@attr.dataclass(frozen=True, hash=True, slots=True, cmp=True)
class Sub:

    maker: str
    episode_num: float
    url: str = attr.ib(converter=fix_url)
    released_at: str = attr.ib(converter=convert_released_dt)


def print_time(t: str) -> str:
    return '{}:{}'.format(t[:2], t[2:])


def encode_url(u: str) -> str:
    prefix = ''
    if u.startswith('http://'):
        prefix = 'http://'
    elif u.startswith('https://'):
        prefix = 'https://'
    return prefix + '/'.join(
        urllib.parse.quote(c) for c in u.replace(prefix, '').split('/')
    )


def make_sub_list(data: set[Sub]) -> list[Attachment]:
    result: list[Attachment] = []

    if data:
        for sub in reversed(
            sorted(list(data), key=lambda x: (x.episode_num, x.released_at))
        ):
            num = '완결' if sub.episode_num == 9999 else f'{sub.episode_num}화'
            name = sub.maker
            url = sub.url
            date = sub.released_at
            if date:
                fallback = f'{num} {date} {name} {url}'
                text = f'{num} {date} {url}'
            else:
                fallback = f'{num} {name} {url}'
                text = f'{num} {url}'
            result.append(
                Attachment(fallback=fallback, author_name=name, text=text)
            )
    else:
        result.append(
            Attachment(fallback='자막 제작자가 없습니다.', text='자막 제작자가 없습니다.')
        )

    return result


@box.command('sub', ['자막', '애니자막'])
@option('--finished/--on-air', '--종영/--방영', '--완결/--방송', '--fin/--on', '-f/-o')
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


async def get_ohli_now_json(timeout: float) -> list[list[dict[str, Any]]]:
    async with async_timeout.timeout(timeout):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://ohli.moe/timetable/list/now'
            ) as resp:
                return json.loads(await resp.text())


async def get_ohli_caption_list(i, timeout: float) -> set[Sub]:
    result: set[Sub] = set()
    async with async_timeout.timeout(timeout):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'https://ohli.moe/timetable/cap?i={i}'
            ) as resp:
                data = await resp.json(loads=json.loads)

    for sub in data:
        episode_num = sub['s']
        if int(math.ceil(episode_num)) == int(episode_num):
            episode_num = int(episode_num)
        result.add(
            Sub(
                maker=sub['n'],
                episode_num=episode_num,
                url=sub['a'],
                released_at=sub['d'],
            )
        )

    return result


async def get_annissa_weekly_json(w, timeout: float) -> list[dict[str, Any]]:
    async with async_timeout.timeout(timeout):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'https://www.anissia.net/anitime/list?w={w}'
            ) as resp:
                return json.loads(await resp.text())


async def get_annissia_caption_list_json(i, timeout: float) -> list[dict]:
    async with async_timeout.timeout(timeout):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'https://www.anissia.net/anitime/cap?i={i}'
            ) as resp:
                return json.loads(await resp.text())


async def search_on_air(bot, event: Message, title: str, timeout: float = 2.5):

    try:
        ohli_all = await get_ohli_now_json(timeout)
    except asyncio.TimeoutError:
        await bot.say(
            event.channel,
            'OHLI 서버가 너무 느려요! 자막 검색이 곤란하니 나중에 다시 시도해주세요!',
        )
        return

    o_data: list[dict[str, Any]] = []

    for w, weekday_list in enumerate(ohli_all):
        for ani in weekday_list:
            ani['week'] = w
            ani['ratio'] = max(
                match(
                    title.lower(),
                    a['s'].lower(),
                )
                for a in ani['n']
            )
            o_data.append(ani)

    o_ani = max(o_data, key=lambda x: x['ratio'])

    if o_ani['ratio'] > 10:
        try:
            a_data = await get_annissa_weekly_json(o_ani['week'], timeout)
        except asyncio.TimeoutError:
            a_data = []

        captions = await get_ohli_caption_list(o_ani['i'], timeout)

        use_anissia = False
        a_ani = None
        if a_data:
            for ani in a_data:
                ani['ratio'] = max(
                    match(alias['s'].lower(), ani['s'].lower())
                    for alias in o_ani['n']
                )

                if o_ani['t'] == ani['t']:
                    ani['ratio'] += 5
                if fuzz.ratio(ani['l'], o_ani['l']) > 90:
                    ani['ratio'] += 10

            a_ani = max(a_data, key=lambda x: x['ratio'])

            if a_ani['ratio'] > 75:
                use_anissia = True

                try:
                    a_subs = await get_annissia_caption_list_json(
                        a_ani['i'],
                        timeout,
                    )
                except asyncio.TimeoutError:
                    a_subs = []
                    use_anissia = False

                for sub in a_subs:
                    url = encode_url(sub['a'])
                    episode_num = int(sub['s']) / 10
                    if int(math.ceil(episode_num)) == int(episode_num):
                        episode_num = int(episode_num)
                    captions.add(
                        Sub(
                            maker=sub['n'],
                            episode_num=episode_num,
                            url=url,
                            released_at=sub['d'],
                        )
                    )

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

        attachments: list[Attachment] = [
            Attachment(
                fallback=fallback,
                title=title,
                title_link=url,
                text=text,
                thumb_url=o_ani['img'] or None,
                pretext=pretext,
            ),
        ]
        attachments.extend(make_sub_list(captions))

        await bot.api.chat.postMessage(
            channel=event.channel,
            attachments=attachments,
            as_user=True,
            thread_ts=event.ts,
        )

    else:
        await bot.say(event.channel, '해당 제목의 애니는 찾을 수 없어요!')


async def search_finished(
    bot,
    event: Message,
    title: str,
    timeout: float = 2.5,
):
    try:
        async with async_timeout.timeout(timeout):
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'http://ohli.moe/timetable/search',
                    params={'query': title},
                ) as resp:
                    data = await resp.json(loads=json.loads)
    except asyncio.TimeoutError:
        await bot.say(event.channel, 'OHLI 서버 상태가 좋지 않아요! 다음에 시도해주세요!')
        return

    if data:
        await bot.say(
            event.channel,
            (f'완결애니를 포함하여 OHLI DB에서 검색한 결과 총 {len(data):,}개의' ' 애니가 검색되었어요!'),
            thread_ts=event.event_ts,
        )
        for ani in data:
            try:
                captions = await get_ohli_caption_list(ani['i'], timeout)
            except asyncio.TimeoutError:
                captions = set()

            attachments: list[Attachment] = [
                Attachment(
                    fallback='*{title}* ({url})'.format(
                        title=ani['s'],
                        url=ani['l'],
                    ),
                    title=ani['s'],
                    title_link=fix_url(ani['l']) if ani['l'] else None,
                    thumb_url=ani['img'] or None,
                ),
            ]
            attachments.extend(make_sub_list(captions))

            await bot.api.chat.postMessage(
                channel=event.channel,
                attachments=attachments,
                as_user=True,
                thread_ts=event.event_ts,
            )
    else:
        await bot.say(
            event.channel,
            '해당 제목의 완결 애니는 찾을 수 없어요!',
        )
