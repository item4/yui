import asyncio
import collections
import datetime
import json
import math
import typing  # noqa: F401

import aiohttp

from fuzzywuzzy import fuzz

from ..box import box
from ..command import argument


Sub = collections.namedtuple(
    'Sub',
    ['maker', 'episode_num', 'url', 'released_at']
)
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


async def get_json(*args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(*args, **kwargs) as res:
            try:
                return await res.json()
            except aiohttp.client_exceptions.ClientResponseError:
                return json.loads(await res.text())


async def get_weekly_list(url, week):
    res = await get_json('{}?w={}'.format(url, week))
    for r in res:
        r['week'] = week
    return res


@box.command('sub', ['애니자막'])
@argument('title', nargs=-1, concat=True, count_error='애니 제목을 입력해주세요')
async def sub(bot, message, title):
    """
    애니메이션 자막을 검색합니다

    OHLI와 애니시아 자막 편성표에서 주어진 제목과 가장 근접한 제목의 애니를 검색하여 보여줍니다.

   `{PREFIX}sub 이나즈마 일레븐` (제목이 `'이나즈마 일레븐'` 에 근접하는 것을 검색)
    `{PREFIX}sub 나 히 아` (제목이 `'나 히 아'` 에 근접하는 것을 검색)

    """

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
        ohli_data.extend(r.result())
    for r in anissia_results:
        anissia_data.extend(r.result())

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

            result: typing.List[Sub] = []

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

            attachments = [
                {
                    'fallback': ('*{title}* ({dow} {time} '
                                 '/ {genre} / {url})').format(
                        title=ohli_ani_result['s'],
                        dow=DOW[ohli_ani_result['week']],
                        time=print_time(ohli_ani_result['t']),
                        genre=anissia_ani_result['g'].replace(' ', ''),
                        url=fix_url(ohli_ani_result['l']),
                    ),
                    'title': ohli_ani_result['s'],
                    'title_link': fix_url(ohli_ani_result['l']),
                    'text': '{dow} {time} / {genre}'.format(
                        dow=DOW[ohli_ani_result['week']],
                        time=print_time(ohli_ani_result['t']),
                        genre=anissia_ani_result['g'].replace(' ', ''),
                    ),
                    'image_url': ohli_ani_result['img'],
                }
            ]
            if result:
                for sub in result:
                    attachments.append({
                        'fallback': '{}화 {} {} {}'.format(
                            sub.episode_num,
                            sub.released_at.strftime(DATE_FORMAT),
                            sub.maker,
                            fix_url(sub.url),
                        ),
                        'author_name': sub.maker,
                        'text': '{}화 {} {}'.format(
                            sub.episode_num,
                            sub.released_at.strftime(DATE_FORMAT),
                            fix_url(sub.url),
                        ),
                    })
            else:
                attachments.append({
                    'fallback': '자막 제작자가 없습니다.',
                    'text': '자막 제작자가 없습니다.',
                })

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
