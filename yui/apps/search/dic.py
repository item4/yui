import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode

from lxml.html import fromstring

from ...bot import Bot
from ...box import box
from ...command import argument, option
from ...event import Message
from ...session import client_session
from ...transform import choice
from ...types.slack.attachment import Attachment

headers: Dict[str, str] = {
    'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0)'
                   ' Gecko/20100101 Firefox/56.0')
}
DICS: Dict[str, str] = {
    '영어': 'eng',
    'English': 'ee',
    '한국어': 'kor',
    '일본어': 'jp',
    '중국어': 'ch',
    '한자': 'hanja',
    '베트남어': 'vi',
    '인도네시아어': 'id',
    '이탈리아어': 'it',
    '프랑스어': 'fr',
    '터키어': 'tr',
    '태국어': 'th',
    '폴란드어': 'pl',
    '포르투갈어': 'pt',
    '체코어': 'cs',
    '헝가리어': 'hu',
    '아랍어': 'ar',
    '스웨덴어': 'sv',
    '힌디어': 'hi',
    '네덜란드어': 'nl',
    '페르시아어': 'fa',
    '스와힐리어': 'sw',
    '루마니아어': 'ro',
    '러시아어': 'ru',
}
BLANK_RE = re.compile(r'^\s+', re.MULTILINE)


def fix_url(url: str) -> str:
    return f'http://dic.daum.net{url}'


def fix_blank(text: str) -> str:
    return BLANK_RE.sub('', text)


def parse(html: str) -> Tuple[Optional[str], List[Attachment]]:
    h = fromstring(html)
    meta = h.cssselect('meta[http-equiv=Refresh]')
    if meta:
        return fix_url(meta[0].get('content')[7:]), []
    else:
        words = h.cssselect('div.search_type')

        attachments: List[Attachment] = []

        for word in words:
            w = word.cssselect('.txt_searchword')[0]
            attachments.append(Attachment(
                title=w.text_content(),
                title_link=fix_url(w.get('href')),
                text=fix_blank(
                    word.cssselect('.list_search')[0].text_content()
                ),
            ))

        return None, attachments


@box.command('dic', ['사전'])
@option('--category', '-c', transform_func=choice(list(DICS.keys())),
        default='영어')
@argument('keyword', nargs=-1, concat=True)
async def dic(bot: Bot, event: Message, category: str, keyword: str):
    """
    다음 사전 검색

    다음 사전에서 입력한 키워드로 검색하여 링크를 보여줍니다.

    `{PREFIX}dic 붕괴` (한영사전에서 `붕괴`로 검색)
    `{PREFIX}dic --category 일본어 붕괴` (일본어사전에서 `붕괴`로 검색)
    `{PREFIX}dic -c English fail` (영영사전에서 `fail`로 검색)

    지원되는 카테고리는 다음과 같습니다.

    * 영어(기본값), English(영영사전), 한국어, 일본어, 중국어, 한자
    * 기타 다음사전에서 지원하는 언어들

    """

    url = 'http://dic.daum.net/search.do?{}'.format(
        urlencode({
            'q': keyword,
            'dic': DICS[category],
        })
    )
    html = ''
    async with client_session() as session:
        async with session.get(url) as res:
            html = await res.text()

    redirect, attachments = await bot.run_in_other_process(parse, html)

    if redirect:
        await bot.say(
            event.channel,
            redirect
        )
    else:
        await bot.api.chat.postMessage(
            channel=event.channel,
            attachments=attachments,
            text='검색결과 {}개의 링크를 찾았어요!'.format(len(attachments)),
            as_user=True,
        )
