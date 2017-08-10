from typing import List  # noqa: F401

import aiohttp

import lxml.html

from ..api import Attachment
from ..box import box
from ..command import argument, option


CATEGORIES = {
    'All': '0_0',
    'Anime': '1_0',
    'Anime-AMV': '1_1',
    'Anime-ET': '1_2',
    'Anime-NET': '1_3',
    'Anime-Raw': '1_4',
    'Audio': '2_0',
    'Audio-Lossless': '2_1',
    'Audio-Lossy': '2_2',
    'Literature': '3_0',
    'Literature-ET': '3_1',
    'Literature-NET': '3_2',
    'Literature-Raw': '3_3',
}


@box.command('nyaa', ['냐'])
@option('--category', '-c', dest='category_name', default='Anime-Raw')
@argument('keyword', nargs=-1, concat=True, count_error='검색어를 입력해주세요')
async def nyaa(bot, message, category_name, keyword):
    """
    냐토렌트에서 주어진 검색어로 파일을 찾습니다

    `{PREFIX}nyaa boku no` (`boku no` 로 시작하는 Anime-Raw를 검색)
    `{PREFIX}nyaa --category=Audio boku no` (`boku no`로 시작하는 Audio를 검색)

    기본 카테고리는 Anime-Raw 이며, 선택 가능한 카테고리는 다음과 같습니다.

    * 전체: All,
    * 아니메: Anime, Anime-AMV, Anime-ET, Anime-NET, Anime-Raw,
    * 음성: Audio, Audio-Lossless, Audio-Lossy,
    * 종이: Literature, Literature-ET, Literature-NET, Literature-Raw

    (ET: English-translated, NET: Non-English-translated)

    """

    try:
        category = CATEGORIES[category_name]
    except KeyError:
        await bot.say(
            message['channel'],
            '지원되지 않는 카테고리에요!'
        )
        return

    html = None

    url = 'https://nyaa.si/?f=0&c={}&q={}'.format(category, keyword)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            html = await res.text()

    h = lxml.html.fromstring(html)

    tr_list = h.cssselect('table.torrent-list > tbody > tr')

    attachments: List[Attachment] = []

    if tr_list:
        for i in range(min(5, len(tr_list))):
            tr = tr_list[i]

            title = tr[1][0].text_content().strip()
            download_link = 'https://nyaa.si{}'.format(tr[2][0].get('href'))

            attachments.append(Attachment(
                fallback='{} - {}'.format(title, download_link),
                title=title,
                title_link='https://nyaa.si{}'.format(tr[1][0].get('href')),
                text=('{} / {} / {}\n'
                      'Seeders: {} / Leechers: {} / Downloads: {}').format(
                    download_link,
                    tr[3].text_content().strip(),
                    tr[4].text_content().strip(),
                    tr[5].text_content().strip(),
                    tr[6].text_content().strip(),
                    tr[7].text_content().strip(),
                )
            ))

        await bot.api.chat.postMessage(
            channel=message['channel'],
            attachments=attachments,
            as_user=True,
        )
    else:
        await bot.say(
            message['channel'],
            '검색결과가 없어요!',
        )
