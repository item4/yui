import asyncio
import logging

import aiohttp
from rapidfuzz import fuzz

from ...bot import Bot
from ...box import box
from ...command import argument
from ...event import Message
from ...event import YuiSystemStart
from ...utils.html import get_root

logger = logging.getLogger(__name__)


REF_URLS: dict[str, str] = {
    "html": "https://developer.mozilla.org/en-US/docs/Web/HTML/Element",
    "css": "https://developer.mozilla.org/en-US/docs/Web/CSS/Reference",
    "python": "https://docs.python.org/3/library/",
}


def parse(
    blob: bytes,
    selector: str,
    url_prefix: str,
) -> list[tuple[str, str]]:
    h = get_root(blob)
    a_tags = h.cssselect(selector)

    result = []
    for a in a_tags:
        name = str(a.text_content())
        link = f"{url_prefix}{a.get('href')}"
        result.append(
            (
                name,
                link,
            ),
        )
    return result


async def fetch_css_ref(bot: Bot):
    logger.info("fetch css ref start")

    url = "https://developer.mozilla.org/en-US/docs/Web/CSS/Reference"
    async with aiohttp.ClientSession() as session, session.get(url) as resp:
        blob = await resp.read()

    body = await bot.run_in_other_process(
        parse,
        blob,
        "a[href^=\\/en-US\\/docs\\/Web\\/CSS\\/]",
        "https://developer.mozilla.org",
    )

    await bot.cache.set("REF_CSS", body)

    logger.info("fetch css ref end")


async def fetch_html_ref(bot: Bot):
    logger.info("fetch html ref start")

    url = "https://developer.mozilla.org/en-US/docs/Web/HTML/Element"
    async with aiohttp.ClientSession() as session, session.get(url) as resp:
        blob = await resp.read()

    body = await bot.run_in_other_process(
        parse,
        blob,
        "a[href^=\\/en-US\\/docs\\/Web\\/HTML\\/Element\\/]",
        "https://developer.mozilla.org",
    )
    await bot.cache.set("REF_HTML", body)

    logger.info("fetch html ref end")


def parse_python(blob: bytes) -> list[tuple[str, str, str]]:
    h = get_root(blob)
    a_tags = h.cssselect("a.reference.internal")

    result = []
    for a in a_tags:
        code_els = a.cssselect("code.docutils.literal")
        name = str(a.text_content()).strip()
        link = f'https://docs.python.org/3/library/{a.get("href")}'
        if code_els:
            result.extend(
                [
                    (
                        str(code_el.text_content()).strip(),
                        name,
                        link,
                    )
                    for code_el in code_els
                ],
            )
        else:
            result.append(
                (
                    "",
                    name,
                    link,
                ),
            )
    return result


async def fetch_python_ref(bot: Bot):
    logger.info("fetch python ref start")

    url = "https://docs.python.org/3/library/"
    async with aiohttp.ClientSession() as session, session.get(url) as resp:
        blob = await resp.read()

    body = await bot.run_in_other_process(
        parse_python,
        blob,
    )

    await bot.cache.set("REF_PYTHON", body)

    logger.info("fetch python ref end")


async def fetch_all_ref(bot):
    tasks = [
        asyncio.create_task(fetch_css_ref(bot)),
        asyncio.create_task(fetch_html_ref(bot)),
        asyncio.create_task(fetch_python_ref(bot)),
    ]
    await asyncio.wait(tasks)


@box.on(YuiSystemStart)
async def on_start(bot):
    logger.info("on_start ref")
    await fetch_all_ref(bot)
    return True


@box.cron("0 3 * * *")
async def refresh(bot):
    logger.info("refresh ref")
    await fetch_all_ref(bot)


@box.command("html", ["htm"])
@argument("keyword", nargs=-1, concat=True, count_error="키워드를 입력해주세요")
async def html(bot, event: Message, keyword: str):
    """
    HTML 레퍼런스 링크

    `{PREFIX}html tbody` (`tbody` TAG에 대한 레퍼런스 링크)

    """

    data = await bot.cache.get("REF_HTML")
    if data is None:
        await bot.say(
            event.channel,
            "아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!",
        )
        return

    name = None
    link = None
    ratio = -100.0
    for _name, _link in data:
        _ratio = fuzz.ratio(keyword, _name)
        if _ratio > ratio:
            name = _name
            link = _link
            ratio = _ratio

    if ratio > 40:
        await bot.say(event.channel, f"HTML `{name}` - {link}")
    else:
        await bot.say(event.channel, "비슷한 HTML Element를 찾지 못하겠어요!")


@box.command("css")
@argument("keyword", nargs=-1, concat=True, count_error="키워드를 입력해주세요")
async def css(bot, event: Message, keyword: str):
    """
    CSS 레퍼런스 링크

    `{PREFIX}css color` (`color` 에 대한 레퍼런스 링크)

    """

    data = await bot.cache.get("REF_CSS")
    if data is None:
        await bot.say(
            event.channel,
            "아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!",
        )
        return

    name = None
    link = None
    ratio = -100.0
    for _name, _link in data:
        _ratio = fuzz.ratio(keyword, _name)
        if _ratio > ratio:
            name = _name
            link = _link
            ratio = _ratio

    if ratio > 40:
        await bot.say(event.channel, f"CSS `{name}` - {link}")
    else:
        await bot.say(event.channel, "비슷한 CSS 관련 요소를 찾지 못하겠어요!")


@box.command("python", ["py"])
@argument("keyword", nargs=-1, concat=True, count_error="키워드를 입력해주세요")
async def python(bot, event: Message, keyword: str):
    """
    Python library 레퍼런스 링크

    `{PREFIX}py re` (`re` 내장 모듈에 대한 레퍼런스 링크)

    """

    data = await bot.cache.get("REF_PYTHON")
    if data is None:
        await bot.say(
            event.channel,
            "아직 레퍼런스 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!",
        )
        return

    name = None
    link = None
    ratio = -100.0
    for code, _name, _link in data:
        _ratio = (
            fuzz.ratio(keyword, code) if code else fuzz.ratio(keyword, _name)
        )
        if _ratio > ratio:
            name = _name
            link = _link
            ratio = _ratio

    if ratio > 40:
        await bot.say(event.channel, f"Python {name} - {link}")
    else:
        await bot.say(event.channel, "비슷한 Python library를 찾지 못하겠어요!")
