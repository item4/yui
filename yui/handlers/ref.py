import re
from typing import Dict

import aiohttp

from fuzzywuzzy import fuzz

from lxml.html import fromstring

from sqlalchemy.orm.exc import NoResultFound

from ..box import box
from ..command import argument
from ..event import Hello, Message
from ..models.ref import Ref


INDEX_NUM_RE = re.compile('^(\d+\.)*.')


REF_URLS: Dict[str, str] = {
    'html': 'https://developer.mozilla.org/en-US/docs/Web/HTML/Element',
    'css': 'https://developer.mozilla.org/en-US/docs/Web/CSS/Reference',
    'python': 'https://docs.python.org/3/library/',
}


async def fetch_ref(name: str, sess):
    url = REF_URLS[name]
    try:
        ref = sess.query(Ref).filter_by(name=name).one()
    except NoResultFound:
        ref = Ref()
        ref.name = name

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            ref.body = await res.text()

    with sess.begin():
        sess.add(ref)


@box.on(Hello)
async def on_start(sess):
    for name in REF_URLS.keys():
        await fetch_ref(name, sess)


@box.crontab('0 0 * * *')
async def on_change_day(sess):
    for name in REF_URLS.keys():
        await fetch_ref(name, sess)


@box.command('html', ['htm'])
@argument('keyword', nargs=-1, concat=True, count_error='키워드를 입력해주세요')
async def html(bot, event: Message, sess, keyword: str):
    """
    HTML 레퍼런스 링크

    `{PREFIX}html tbody` (`tbody` TAG에 대한 레퍼런스 링크)

    """

    try:
        ref = sess.query(Ref).filter_by(name='html').one()
    except NoResultFound:
        await bot.say(
            event.channel,
            '아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!'
        )
        return

    h = fromstring(ref.body)
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
async def css(bot, event: Message, sess, keyword: str):
    """
    CSS 레퍼런스 링크

    `{PREFIX}css color` (`color` 에 대한 레퍼런스 링크)

    """

    try:
        ref = sess.query(Ref).filter_by(name='css').one()
    except NoResultFound:
        await bot.say(
            event.channel,
            '아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!'
        )
        return

    h = fromstring(ref.body)
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

    async with aiohttp.ClientSession() as session:
        for url in urls:
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


@box.command('python', ['py'])
@argument('keyword', nargs=-1, concat=True, count_error='키워드를 입력해주세요')
async def python(bot, event: Message, sess, keyword: str):
    """
    Python library 레퍼런스 링크

    `{PREFIX}py re` (`re` 내장 모듈에 대한 레퍼런스 링크)

    """

    try:
        ref = sess.query(Ref).filter_by(name='python').one()
    except NoResultFound:
        await bot.say(
            event.channel,
            '아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!'
        )
        return

    h = fromstring(ref.body)
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
