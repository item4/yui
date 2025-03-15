import asyncio
import datetime
import functools
from typing import Final

import aiohttp
import aiohttp.client_exceptions
from defusedxml import ElementTree
from yarl import URL

from ..box import box
from ..command.cooltime import Cooltime
from ..event import Message
from ..utils import json
from ..utils.html import get_root

DEFAULT_COOLTIME = datetime.timedelta(minutes=30)
DM_COOLTIME = datetime.timedelta(minutes=3)

CAT_API_URL: Final[URL] = URL(
    "https://thecatapi.com/api/images/get",
).with_query(
    format="xml",
    type="jpg,png",
)
DOG_API_URL: Final[str] = "https://dog.ceo/api/breeds/image/random"
FOX_GALLERY_URL: Final[str] = "http://fox-info.net/fox-gallery"


class APIServerError(RuntimeError):
    pass


async def get_cat_image_url(timeout: float) -> str:  # noqa: ASYNC109
    api_url = "https://thecatapi.com/api/images/get"
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(
                    api_url,
                    params={"format": "xml", "type": "jpg,png"},
                ) as resp:
                    if resp.status != 200:
                        raise APIServerError
                    xml_result = await resp.read()
                    tree = ElementTree.fromstring(xml_result)
                    url = tree.find("data/images/image/url").text
            except aiohttp.client_exceptions.ServerDisconnectedError:
                await asyncio.sleep(0.1)
                continue
            try:
                async with (
                    asyncio.timeout(delay=timeout),
                    session.get(
                        url,
                    ) as resp,
                    resp,
                ):
                    if resp.status == 200:
                        return url
            except (aiohttp.ClientConnectorError, TimeoutError):
                continue


async def get_dog_image_url(timeout: float) -> str:  # noqa: ASYNC109
    api_url = "https://dog.ceo/api/breeds/image/random"
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(api_url) as resp:
                    if resp.status != 200:
                        raise APIServerError
                    data = await resp.json(loads=json.loads)
                    url = data["message"]
            except aiohttp.client_exceptions.ServerDisconnectedError:
                await asyncio.sleep(0.1)
                continue
            try:
                async with (
                    asyncio.timeout(delay=timeout),
                    session.get(
                        url,
                    ) as resp,
                    resp,
                ):
                    if resp.status == 200:
                        return url
            except (aiohttp.ClientConnectorError, TimeoutError):
                continue


async def get_fox_image_url(timeout: float) -> str:  # noqa: ASYNC109
    url = "http://fox-info.net/fox-gallery"
    async with (
        asyncio.timeout(
            delay=timeout,
        ),
        aiohttp.ClientSession() as session,
        session.get(url) as resp,
    ):
        data = await resp.text()
    h = get_root(data)
    image_els = h.cssselect("#gallery-1 img.attachment-thumbnail")
    try:
        return str(image_els[0].get("src"))
    except IndexError as e:
        raise APIServerError from e


@box.command("cat", ["냥", "야옹", "냐옹"])
async def cat(bot: Bot, event: Message, timeout: float = 1.5):  # noqa: ASYNC109
    """
    냥냥이 짤을 수급합니다.
    쿨타임은 일반 채널 30분, DM 3분입니다.

    `{PREFIX}cat`: 냐짤 수급

    """
    cat_say = functools.partial(
        bot.api.chat.postMessage,
        channel=event.channel,
        username="냥짤의 요정",
        icon_url="https://i.imgur.com/hIBJUMI.jpg",
    )

    cooltime = Cooltime(
        bot=bot,
        key=f"YUI_APPS_ANIMAL_CAT_{event.channel}",
        cooltime=(
            DM_COOLTIME if event.channel.startswith("D") else DEFAULT_COOLTIME
        ),
    )
    if retry_after := await cooltime.rejected():
        await cat_say(
            text=(
                f"아직 쿨타임이다냥! {retry_after.strftime('%H시 %M분')} 이후로"
                " 다시 시도해보라냥!"
            ),
        )
        return

    try:
        url = await get_cat_image_url(timeout)
    except APIServerError:
        await cat_say(
            text="냥냥이 API 서버의 상태가 좋지 않다냥! 나중에 다시 시도해보라냥!",
        )
        return

    await cooltime.record()

    await cat_say(text=url)


@box.command("dog", ["멍"])
async def dog(bot, event: Message, timeout: float = 1.5):  # noqa: ASYNC109
    """
    멍멍이 짤을 수급합니다.

    쿨타임은 일반 채널 30분, DM 3분입니다.

    `{PREFIX}dog`: 멍짤 수급

    """

    dog_say = functools.partial(
        bot.api.chat.postMessage,
        channel=event.channel,
        username="멍짤의 요정",
        icon_url="https://i.imgur.com/Q9FKplO.png",
    )

    cooltime = Cooltime(
        bot=bot,
        key=f"YUI_APPS_ANIMAL_DOG_{event.channel}",
        cooltime=(
            DM_COOLTIME if event.channel.startswith("D") else DEFAULT_COOLTIME
        ),
    )
    if retry_after := await cooltime.rejected():
        await dog_say(
            text=(
                f"아직 쿨타임이다멍! {retry_after.strftime('%H시 %M분')} 이후로"
                " 다시 시도해보라멍!"
            ),
        )
        return

    try:
        url = await get_dog_image_url(timeout)
    except APIServerError:
        await dog_say(
            text="멍멍이 API 서버의 상태가 좋지 않다멍! 나중에 다시 시도해보라멍!",
        )
        return

    await cooltime.record()

    await dog_say(text=url)


@box.command("fox", ["여우"])
async def fox(bot, event: Message, timeout: float = 1.5):  # noqa: ASYNC109
    """
    여우 짤을 수급합니다.

    쿨타임은 일반 채널 30분, DM 3분입니다.

    `{PREFIX}fox`: 여우짤 수급

    """

    fox_say = functools.partial(
        bot.api.chat.postMessage,
        channel=event.channel,
        username="웹 브라우저의 요정",
        icon_url="https://i.imgur.com/xFpyvpZ.png",
    )

    cooltime = Cooltime(
        bot=bot,
        key=f"YUI_APPS_ANIMAL_FOX_{event.channel}",
        cooltime=(
            DM_COOLTIME if event.channel.startswith("D") else DEFAULT_COOLTIME
        ),
    )
    if retry_after := await cooltime.rejected():
        await fox_say(
            text=(
                f"아직 쿨타임이에요! {retry_after.strftime('%H시 %M분')} 이후로"
                " 다시 시도해보세요!"
            ),
        )
        return

    try:
        url = await get_fox_image_url(timeout)
    except APIServerError:
        await fox_say(
            text="여우짤 서버의 상태가 좋지 않네요! 나중에 다시 시도해보세요!",
        )
        return

    await cooltime.record()

    await fox_say(text=url)
