import asyncio
import functools
import logging
import re
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, Tuple

from fuzzywuzzy import fuzz

from lxml.html import fromstring

from sqlalchemy.orm.exc import NoResultFound

from ..box import box
from ..command import argument
from ..event import ChatterboxSystemStart, Message
from ..models.cache import JSONCache
from ..session import client_session
from ..util import now

logger = logging.getLogger(__name__)

INDEX_NUM_RE = re.compile('^(\d+\.)*.')


REF_URLS: Dict[str, str] = {
    'html': 'https://developer.mozilla.org/en-US/docs/Web/HTML/Element',
    'css': 'https://developer.mozilla.org/en-US/docs/Web/CSS/Reference',
    'python': 'https://docs.python.org/3/library/',
}


def fetch_or_create_cache(name: str, sess) -> JSONCache:
    try:
        ref = sess.query(JSONCache).filter_by(name=name).one()
    except NoResultFound:
        ref = JSONCache()
        ref.name = name
    return ref


def parse(html: str, selector: str, url_prefix: str) -> List[Tuple[str, str]]:
    h = fromstring(html)
    a_tags = h.cssselect(selector)

    result = []
    for a in a_tags:
        name = a.text_content()
        link = f"{url_prefix}{a.get('href')}"
        result.append((
            name,
            link,
        ))
    return result


async def fetch_css_ref(loop, sess):
    logger.info(f'fetch css ref start')

    ref = fetch_or_create_cache('css', sess)

    url = 'https://developer.mozilla.org/en-US/docs/Web/CSS/Reference'
    async with client_session() as session:
        async with session.get(url) as res:
            html = await res.text()

    with ProcessPoolExecutor() as ex:
        body = await loop.run_in_executor(ex, functools.partial(
            parse,
            html,
            'a[href^=\\/en-US\\/docs\\/Web\\/CSS\\/]',
            'https://developer.mozilla.org',
        ))

    ref.body = body
    ref.created_at = now()

    with sess.begin():
        sess.add(ref)

    logger.info(f'fetch css ref end')


async def fetch_html_ref(loop, sess):
    logger.info(f'fetch html ref start')

    ref = fetch_or_create_cache('html', sess)

    url = 'https://developer.mozilla.org/en-US/docs/Web/HTML/Element'
    async with client_session() as session:
        async with session.get(url) as res:
            html = await res.text()

    with ProcessPoolExecutor() as ex:
        body = await loop.run_in_executor(ex, functools.partial(
            parse,
            html,
            'a[href^=\\/en-US\\/docs\\/Web\\/HTML\\/Element\\/]',
            'https://developer.mozilla.org'
        ))

    ref.body = body
    ref.created_at = now()

    with sess.begin():
        sess.add(ref)

    logger.info(f'fetch html ref end')


def parse_python(html: str) -> List[Tuple[str, str, str]]:
    h = fromstring(html)
    a_tags = h.cssselect('a.reference.internal')

    result = []
    for a in a_tags:
        code = ''
        code_el = a.cssselect('code.docutils.literal')
        name = INDEX_NUM_RE.sub('', a.text_content())
        link = f'https://docs.python.org/3/library/{a.get("href")}'
        if code_el:
            code = str(code_el[0].text_content())
        result.append((
            code,
            name,
            link,
        ))
    return result


async def fetch_python_ref(loop, sess):
    logger.info(f'fetch python ref start')

    ref = fetch_or_create_cache('python', sess)

    url = 'https://docs.python.org/3/library/'
    async with client_session() as session:
        async with session.get(url) as res:
            html = await res.text()

    with ProcessPoolExecutor() as ex:
        body = await loop.run_in_executor(ex, functools.partial(
            parse_python,
            html,
        ))

    ref.body = body
    ref.created_at = now()

    with sess.begin():
        sess.add(ref)

    logger.info(f'fetch python ref end')


@box.on(ChatterboxSystemStart)
async def on_start(loop, sess):
    logger.info('on_start ref')
    tasks = [
        fetch_css_ref(loop, sess),
        fetch_html_ref(loop, sess),
        fetch_python_ref(loop, sess),
    ]
    await asyncio.wait(tasks)
    return True


@box.crontab('0 3 * * *')
async def refresh(loop, sess):
    logger.info('refresh ref')
    tasks = [
        fetch_css_ref(loop, sess),
        fetch_html_ref(loop, sess),
        fetch_python_ref(loop, sess),
    ]
    await asyncio.wait(tasks)


@box.command('html', ['htm'])
@argument('keyword', nargs=-1, concat=True, count_error='키워드를 입력해주세요')
async def html(bot, event: Message, sess, keyword: str):
    """
    HTML 레퍼런스 링크

    `{PREFIX}html tbody` (`tbody` TAG에 대한 레퍼런스 링크)

    """

    try:
        ref = sess.query(JSONCache).filter_by(name='html').one()
    except NoResultFound:
        await bot.say(
            event.channel,
            '아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!'
        )
        return

    name = None
    link = None
    ratio = -1
    for _name, _link in ref.body:
        _ratio = fuzz.ratio(keyword, _name)
        if _ratio > ratio:
            name = _name
            link = _link
            ratio = _ratio

    if ratio > 40:
        await bot.say(
            event.channel,
            f':html: `{name}` - {link}'
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
        ref = sess.query(JSONCache).filter_by(name='css').one()
    except NoResultFound:
        await bot.say(
            event.channel,
            '아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!'
        )
        return

    name = None
    link = None
    ratio = -1
    for _name, _link in ref.body:
        _ratio = fuzz.ratio(keyword, _name)
        if _ratio > ratio:
            name = _name
            link = _link
            ratio = _ratio

    if ratio > 40:
        await bot.say(
            event.channel,
            f':css: `{name}` - {link}'
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

    async with client_session() as session:
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
        ref = sess.query(JSONCache).filter_by(name='python').one()
    except NoResultFound:
        await bot.say(
            event.channel,
            '아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!'
        )
        return

    name = None
    link = None
    ratio = -1
    for code, _name, _link in ref.body:
        if code:
            _ratio = fuzz.ratio(keyword, code)
        else:
            _ratio = fuzz.ratio(keyword, _name)
        if _ratio > ratio:
            name = _name
            link = _link
            ratio = _ratio

    if ratio > 40:
        await bot.say(
            event.channel,
            f':python: {name} - {link}'
        )
    else:
        await bot.say(
            event.channel,
            '비슷한 Python library를 찾지 못하겠어요!'
        )
