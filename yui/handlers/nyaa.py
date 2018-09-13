import datetime
from typing import List
from urllib.parse import urlencode

from pyppeteer.errors import TimeoutError

import tzlocal

from ..api import Action, Attachment
from ..box import box
from ..browser import new_page
from ..command import argument, option
from ..event import Message
from ..transform import choice


CATEGORIES = {
    'all': '0_0',
    'anime': '1_0',
    'anime-amv': '1_1',
    'anime-et': '1_2',
    'anime-net': '1_3',
    'anime-raw': '1_4',
    'audio': '2_0',
    'audio-lossless': '2_1',
    'audio-lossy': '2_2',
    'literature': '3_0',
    'literature-et': '3_1',
    'literature-net': '3_2',
    'literature-raw': '3_3',
}

SCRIPT = '''
(tr_list) => {
    return tr_list.map((tr) => {
        const title_td = tr.children[1];
        const last_el_index = title_td.children.length - 1;
        const title = title_td.children[last_el_index].textContent;
        const page_url = tr.children[1].children[0].href;
        const download_url = tr.children[2].children[0].href;
        const magnet_url = tr.children[2].children[1].href;
        const size = tr.children[3].textContent;
        const uploaded_at = Number(tr.children[4].dataset.timestamp);
        const seeders = tr.children[5].textContent;
        const leechers = tr.children[6].textContent;
        const downloads = tr.children[7].textContent;
        return {
            title,
            page_url,
            download_url,
            magnet_url,
            size,
            uploaded_at,
            seeders,
            leechers,
            downloads,
        }
    });
}
'''

CONTAINER_SELECTOR = 'div.container'
NOT_FOUND_SELECTOR = 'div.container h3'
TABLE_ROW_SELECTOR = 'table.torrent-list > tbody > tr'


@box.command('nyaa', ['냐'])
@option('--category', '-c', dest='category_name',
        default='anime-raw', transform_error='지원되지 않는 카테고리에요!',
        transform_func=choice(
            list(CATEGORIES.keys()),
            case_insensitive=True,
            case='lower'))
@argument('keyword', nargs=-1, concat=True, count_error='검색어를 입력해주세요')
async def nyaa(
    bot,
    event: Message,
    category_name: str,
    keyword: str
):
    """
    일본 서브컬처 토렌트 사이트 냐토렌트에서 주어진 검색어로 파일을 찾습니다

    `{PREFIX}nyaa boku no` (`boku no` 로 시작하는 Anime-Raw를 검색)
    `{PREFIX}nyaa --category=Audio boku no` (`boku no`로 시작하는 Audio를 검색)

    기본 카테고리는 Anime-Raw 이며, 선택 가능한 카테고리는 다음과 같습니다.

    * 전체: All,
    * 아니메: Anime, Anime-AMV, Anime-ET, Anime-NET, Anime-Raw,
    * 음성: Audio, Audio-Lossless, Audio-Lossy,
    * 종이: Literature, Literature-ET, Literature-NET, Literature-Raw

    (ET: English-translated, NET: Non-English-translated)

    Fab(sukebei) 검색은 지원하지 않습니다.

    """

    category = CATEGORIES[category_name]

    url = 'https://nyaa.si/?{}'.format(urlencode({
        'f': '0',
        'c': category,
        'q': keyword,
    }))

    async with new_page(bot) as page:
        await page.goto(url)
        try:
            await page.waitForSelector(CONTAINER_SELECTOR)
        except TimeoutError:
            await bot.say(
                event.channel,
                'nyaa 접속에 실패했어요!'
            )
            return

        not_found_tag = await page.querySelector(NOT_FOUND_SELECTOR)
        if not_found_tag is None:
            result = await page.querySelectorAllEval(
                TABLE_ROW_SELECTOR,
                SCRIPT,
            )
        else:
            result = []

    attachments: List[Attachment] = []

    for i in range(min(7, len(result))):
        row = result[i]
        actions: List[Action] = [Action(
            type='button',
            text='Download',
            url=row['download_url'],
        ), Action(
            type='button',
            text='Magnet Link',
            url=row['magnet_url'],
        )]

        attachments.append(Attachment(
            fallback='{} - {}'.format(row['title'], row['download_url']),
            title=row['title'],
            title_link=row['page_url'],
            actions=actions,
            text=('{} / {}\n'
                  'Seeders: {} / Leechers: {} / Downloads: {}').format(
                row['size'],
                datetime.datetime.fromtimestamp(
                    row['uploaded_at'],
                    tz=tzlocal.get_localzone(),
                ).strftime('%Y-%m-%d %H:%M'),
                row['seeders'],
                row['leechers'],
                row['downloads'],
            )
        ))

    if attachments:
        await bot.api.chat.postMessage(
            channel=event.channel,
            attachments=attachments,
            as_user=True,
            thread_ts=event.ts,
        )
    else:
        await bot.say(
            event.channel,
            '검색결과가 없어요!',
        )
