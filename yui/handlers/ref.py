import re

import aiohttp

from fuzzywuzzy import fuzz

from lxml.html import fromstring

from ..box import box
from ..command import argument
from ..event import Message


INDEX_NUM_RE = re.compile('^(\d+\.)*.')


@box.command('html', ['htm'])
@argument('keyword', nargs=-1, concat=True, count_error='키워드를 입력해주세요')
async def html(bot, event: Message, keyword: str):
    """
    HTML 레퍼런스 링크

    `{PREFIX}html tbody` (`tbody` TAG에 대한 레퍼런스 링크)

    """

    html = ''
    url = 'https://developer.mozilla.org/en-US/docs/Web/HTML/Element'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            html = await res.text()

    h = fromstring(html)
    a_tags = h.cssselect('a[href^=\\/en-US\\/docs\\/Web\\/HTML\\/Element\\/]')

    name = None
    link = None
    ratio = -1
    for a in a_tags:
        _name = a.text_content()
        _link = a.get('href')
        _ratio = fuzz.ratio(keyword, _name)
        if _ratio > ratio:
            name = _name
            link = _link
            ratio = _ratio

    if ratio > 40:
        await bot.say(
            event.channel,
            f':html: `{name}` - https://developer.mozilla.org{link}'
        )
    else:
        await bot.say(
            event.channel,
            '비슷한 HTML Element를 찾지 못하겠어요!'
        )


@box.command('css')
@argument('keyword', nargs=-1, concat=True, count_error='키워드를 입력해주세요')
async def css(bot, event: Message, keyword: str):
    """
    CSS 레퍼런스 링크

    `{PREFIX}css color` (`color` 에 대한 레퍼런스 링크)

    """

    html = ''
    url = 'https://developer.mozilla.org/en-US/docs/Web/CSS/Reference'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            html = await res.text()

    h = fromstring(html)
    a_tags = h.cssselect('a[href^=\\/en-US\\/docs\\/Web\\/CSS\\/]')

    name = None
    link = None
    ratio = -1
    for a in a_tags:
        _name = a.text_content()
        _link = a.get('href')
        _ratio = fuzz.ratio(keyword, _name)
        if _ratio > ratio:
            name = _name
            link = _link
            ratio = _ratio

    if ratio > 40:
        await bot.say(
            event.channel,
            f':css: `{name}` - https://developer.mozilla.org{link}'
        )
    else:
        await bot.say(
            event.channel,
            '비슷한 CSS 관련 요소를 찾지 못하겠어요!'
        )


@box.command('php')
@argument('keyword', nargs=-1, concat=True, count_error='키워드를 입력해주세요')
async def php(bot, event: Message, keyword: str):
    """
    PHP 레퍼런스 링크

    `{PREFIX}php json_encode` (`json_encode` 에 대한 레퍼런스 링크)

    """

    raw_path = keyword.replace('::', '.')
    if '::' in keyword:
        superclass, func = keyword \
            .lower()\
            .replace('$', '')\
            .replace('__', '')\
            .replace('_', '-')\
            .split('::')
    elif keyword.startswith('mysqli_stmt_'):
        superclass = 'mysqli-stmt'
        func = keyword[12:].replace('_', '-')
    elif keyword.startswith('mysqli_'):
        superclass = 'mysqli'
        func = keyword[7:].replace('_', '-')
    else:
        superclass, func = 'function', keyword \
            .lower()\
            .replace('$', '')\
            .replace('__', '')\
            .replace('_', '-')

    urls = [
        f'http://www.php.net/manual/en/{superclass}.{func}.php',
        f'http://php.net/{raw_path}',
    ]

    for url in urls:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                async with res:
                    res_url = str(res.url)
                    if 'manual-lookup.php' in res_url:
                        continue
                    if res.status == 200:
                        await bot.say(
                            event.channel,
                            f':php: `{keyword}` - {res_url}'
                        )
                        break
    else:
        await bot.say(
            event.channel,
            '비슷한 PHP 관련 요소를 찾지 못하겠어요!'
        )


@box.command('py', ['python'])
@argument('keyword', nargs=-1, concat=True, count_error='키워드를 입력해주세요')
async def py(bot, event: Message, keyword: str):
    """
    Python library 레퍼런스 링크

    `{PREFIX}py re` (`re` 내장 모듈에 대한 레퍼런스 링크)

    """

    html = ''
    url = 'https://docs.python.org/3/library/'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            html = await res.text()

    h = fromstring(html)
    a_tags = h.cssselect('a.reference.internal')

    name = None
    link = None
    ratio = -1
    for a in a_tags:
        code = a.cssselect('code.docutils.literal')
        _name = INDEX_NUM_RE.sub('', a.text_content())
        _link = a.get('href')
        if code:
            _ratio = fuzz.ratio(keyword, code[0].text_content())
        else:
            _ratio = fuzz.ratio(keyword, _name)
        if _ratio > ratio:
            name = _name
            link = _link
            ratio = _ratio

    if ratio > 40:
        await bot.say(
            event.channel,
            f':python: {name} - https://docs.python.org/3/library/{link}'
        )
    else:
        await bot.say(
            event.channel,
            '비슷한 Python library를 찾지 못하겠어요!'
        )
