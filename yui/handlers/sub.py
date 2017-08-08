import asyncio
import datetime
import json
import math
import urllib.parse

from typing import List, NamedTuple

import aiohttp

from fuzzywuzzy import fuzz

from ..api import Attachment
from ..box import box
from ..command import argument, option


class Sub(NamedTuple):

    maker: str
    episode_num: float
    url: str
    released_at: datetime.datetime


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


def fix_url(url: str) -> str:
    if url.startswith('https://') or url.startswith('http://'):
        return url
    return 'http://{}'.format(url)


def make_sub_list(data: List[Sub]) -> List[Attachment]:
    result: List[Attachment] = []

    if data:
        for sub in data:
            result.append(
                Attachment(
                    fallback='{}화 {} {} {}'.format(
                        sub.episode_num,
                        sub.released_at.strftime(DATE_FORMAT),
                        sub.maker,
                        fix_url(sub.url),
                    ),
                    author_name=sub.maker,
                    text='{}화 {} {}'.format(
                        sub.episode_num,
                        sub.released_at.strftime(DATE_FORMAT),
                        fix_url(sub.url),
                    ),
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


async def get_json(*args, **kwargs):
    weight = 1
    while True:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(*args, **kwargs) as res:
                    try:
                        return await res.json()
                    except aiohttp.client_exceptions.ClientResponseError:
                        return json.loads(await res.text())
            except aiohttp.client_exceptions.ServerDisconnectedError:
                await asyncio.sleep(weight/10)
                weight += 1


async def get_weekly_list(url, week):
    weight = 1
    while True:
        res = await get_json('{}?w={}'.format(url, week))
        if res:
            for r in res:
                r['week'] = week
            return res
        await asyncio.sleep(weight/10)
        weight += 1


@box.command('sub', ['애니자막'])
@option('--finished/--on-air', '--종영/--방영', '--fin/--on', '-f/-o')
@argument('title', nargs=-1, concat=True, count_error='애니 제목을 입력해주세요')
async def sub(bot, message, finished, title):
    """
    애니메이션 자막을 검색합니다

    OHLI와 애니시아 자막 편성표에서 주어진 제목과 가장 근접한 제목의 애니를 검색하여 보여줍니다.

    방영중 애니 검색은 기본적으로 OHLI의 자막 목록에서 fuzzy search 후, OHLI에서 제공하는
    ALIAS를 기준으로 삼아 애니시아의 자막 목록에서 검색합니다. 따라서 OHLI와 애니시아의 애니명이
    다른 경우에는 검색이 가능하지만, OHLI에 아예 없는 애니는 검색이 불가능합니다.

    종영 애니 검색은 OHLI만을 검색합니다. OHLI의 검색 API를 이용하기 때문에 fuzzy search 를
    지원하지 않습니다.

    `{PREFIX}sub 이나즈마 일레븐` (제목이 `'이나즈마 일레븐'` 에 근접하는 것을 검색)
    `{PREFIX}sub 나 히 아` (제목이 `'나 히 아'` 에 근접하는 것을 검색)
    `{PREFIX}sub --finished aldnoah` (제목에 `'aldnoah'`가 들어가는 완결 애니를 검색)

    """

    if finished:
        await search_finished(bot, message, title)
    else:
        await search_on_air(bot, message, title)


async def search_on_air(bot, message, title):

    ohli = []
    anissia = []
    for w in range(7+1):
        ohli.append(
            get_weekly_list('http://ohli.moe/anitime/list', w)
        )
        anissia.append(
            get_weekly_list('http://www.anissia.net/anitime/list', w)
        )

    ohli_results, _ = await asyncio.wait(ohli)
    anissia_results, _ = await asyncio.wait(anissia)
    ohli_data = []
    anissia_data = []

    for r in ohli_results:
        try:
            res = r.result()
        except Exception as e:
            await bot.say(
                message['channel'],
                'Error: {}: {}'.format(e.__class__.__name__, e)
            )
            return
        else:
            ohli_data.extend(res)
    for r in anissia_results:
        try:
            res = r.result()
        except Exception as e:
            await bot.say(
                message['channel'],
                'Error: {}: {}'.format(e.__class__.__name__, e)
            )
            return
        else:
            anissia_data.extend(res)

    for ani in ohli_data:
        ani['ratio'] = max(
            fuzz.ratio(title.lower(), a['s'].lower()) for a in ani['n']
        )

    ohli_data.sort(key=lambda x: x['ratio'], reverse=True)

    ohli_ani_result = ohli_data[0]

    if ohli_ani_result['ratio'] > 10:
        for ani in anissia_data:
            ani['ratio'] = max(
                fuzz.ratio(a['s'].lower(), ani['s'].lower())
                for a in ohli_ani_result['n']
            )

        anissia_data.sort(key=lambda x: x['ratio'], reverse=True)
        anissia_ani_result = anissia_data[0]

        if anissia_ani_result['ratio'] > 80:
            ohli_sub_result = await get_json(
                'http://ohli.moe/timetable/cap?i={}'.format(
                    ohli_ani_result['i']
                )
            )
            anissia_sub_result = await get_json(
                'http://www.anissia.net/anitime/cap?i={}'.format(
                    anissia_ani_result['i']
                )
            )

            for sub in anissia_sub_result:
                if ohli_sub_result:
                    sub['duplicated'] = max(
                        fuzz.ratio(sub['a'].lower(), s['a'].lower())
                        for s in ohli_sub_result
                    ) > 95
                else:
                    sub['duplicated'] = False

            result: List[Sub] = []

            for sub in ohli_sub_result:
                episode_num = sub['s']
                if sub['d'] == '00000000000000':
                    released_at = datetime.datetime.min
                else:
                    released_at = datetime.datetime.strptime(
                        sub['d'],
                        '%Y%m%d%H%M%S'
                    )
                if int(math.ceil(episode_num)) == int(episode_num):
                    episode_num = int(episode_num)
                result.append(Sub(
                    maker=sub['n'],
                    episode_num=episode_num,
                    url=sub['a'],
                    released_at=released_at,
                ))

            for sub in anissia_sub_result:
                if sub['duplicated']:
                    continue
                episode_num = int(sub['s'])/10
                if sub['d'] == '00000000000000':
                    released_at = datetime.datetime.min
                else:
                    released_at = datetime.datetime.strptime(
                        sub['d'],
                        '%Y%m%d%H%M%S'
                    )
                if int(math.ceil(episode_num)) == int(episode_num):
                    episode_num = int(episode_num)
                result.append(Sub(
                    maker=sub['n'],
                    episode_num=episode_num,
                    url=sub['a'],
                    released_at=released_at,
                ))

            attachments: List[Attachment] = [
                Attachment(
                    fallback=('*{title}* ({dow} {time} '
                              '/ {genre} / {url})').format(
                        title=ohli_ani_result['s'],
                        dow=DOW[ohli_ani_result['week']],
                        time=print_time(ohli_ani_result['t']),
                        genre=anissia_ani_result['g'].replace(' ', ''),
                        url=fix_url(ohli_ani_result['l']),
                    ),
                    title=ohli_ani_result['s'],
                    title_link=fix_url(ohli_ani_result['l'])
                    if ohli_ani_result['l'] else None,
                    text='{dow} {time} / {genre}'.format(
                        dow=DOW[ohli_ani_result['week']],
                        time=print_time(ohli_ani_result['t']),
                        genre=anissia_ani_result['g'].replace(' ', ''),
                    ),
                    thumb_url=ohli_ani_result['img'] or None,
                ),
            ]
            attachments.extend(make_sub_list(result))

            await bot.api.chat.postMessage(
                channel=message['channel'],
                attachments=attachments,
                as_user=True,
            )
        else:
            await bot.say(
                message['channel'],
                '입력해주신 키워드로 애니메이션 제목을 특정하지 못하겠어요! '
                'OHLI에선 {}, Anissia에선 {}이(가) 가장 비슷한 것으로 보여요.'.format(
                    ohli_ani_result['s'],
                    anissia_ani_result['s']
                )
            )
    else:
        await bot.say(
            message['channel'],
            '해당 제목의 애니는 찾을 수 없어요!'
        )


async def search_finished(bot, message, title):

    data = await get_json(
        'http://ohli.moe/timetable/search?{}'.format(
            urllib.parse.urlencode({'query': title.encode()})
        )
    )
    print('http://ohli.moe/timetable/search?{}'.format(
        urllib.parse.urlencode({'query': title.encode()})
    ))

    filtered = list(filter(lambda x: x['status'] == '완', data))

    if filtered:
        ani = filtered[0]
        subs = await get_json(
            'http://ohli.moe/timetable/cap?i={}'.format(ani['i']))
        result: List[Sub] = []

        for sub in subs:
            episode_num = sub['s']
            if sub['d'] == '00000000000000':
                released_at = datetime.datetime.min
            else:
                released_at = datetime.datetime.strptime(
                    sub['d'],
                    '%Y%m%d%H%M%S'
                )
            if int(math.ceil(episode_num)) == int(episode_num):
                episode_num = int(episode_num)
            result.append(Sub(
                maker=sub['n'],
                episode_num=episode_num,
                url=sub['a'],
                released_at=released_at,
            ))

        attachments: List[Attachment] = [
            Attachment(
                fallback=('*{title}* ({url})').format(
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
            channel=message['channel'],
            attachments=attachments,
            as_user=True,
        )
    else:
        await bot.say(
            message['channel'],
            '해당 제목의 완결 애니는 찾을 수 없어요!',
        )
