import asyncio
import datetime
import functools

import aiohttp
import aiohttp.client_exceptions

import async_timeout

from lxml import etree
from lxml import html

from ..box import box
from ..command import option
from ..event import Message
from ..types.channel import DirectMessageChannel
from ..utils import json
from ..utils.datetime import now

DEFAULT_COOLTIME = datetime.timedelta(minutes=30)
DM_COOLTIME = datetime.timedelta(minutes=3)


class APIServerError(RuntimeError):
    pass


async def get_cat_image_url(timeout: float) -> str:
    api_url = 'http://thecatapi.com/api/images/get'
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(
                    api_url, params={'format': 'xml', 'type': 'jpg,png'}
                ) as res:
                    if res.status != 200:
                        raise APIServerError
                    xml_result = await res.read()
                    tree = etree.fromstring(xml_result)
                    url = tree.find('data/images/image/url').text
            except aiohttp.client_exceptions.ServerDisconnectedError:
                await asyncio.sleep(0.1)
                continue
            try:
                async with async_timeout.timeout(timeout=timeout):
                    async with session.get(url) as res:
                        async with res:
                            if res.status == 200:
                                return url
            except (aiohttp.ClientConnectorError, asyncio.TimeoutError):
                continue


async def get_dog_image_url(timeout: float) -> str:
    api_url = 'https://dog.ceo/api/breeds/image/random'
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(api_url) as res:
                    if res.status != 200:
                        raise APIServerError
                    data = await res.json(loads=json.loads)
                    url = data['message']
            except aiohttp.client_exceptions.ServerDisconnectedError:
                await asyncio.sleep(0.1)
                continue
            try:
                async with async_timeout.timeout(timeout=timeout):
                    async with session.get(url) as res:
                        async with res:
                            if res.status == 200:
                                return url
            except (aiohttp.ClientConnectorError, asyncio.TimeoutError):
                continue


async def get_fox_image_url(timeout: float) -> str:
    url = 'http://fox-info.net/fox-gallery'
    async with async_timeout.timeout(timeout=timeout):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.text()
    h = html.fromstring(data)
    image_els = h.cssselect('#gallery-1 img.attachment-thumbnail')
    try:
        return str(image_els[0].get('src'))
    except IndexError:
        raise APIServerError


@box.command('cat', ['냥', '야옹', '냐옹'])
@option('--timeout', default=1.5)
async def cat(bot, event: Message, timeout: float):
    """
    냥냥이 짤을 수급합니다.
    쿨타임은 일반 채널 30분, DM 3분입니다.

    `{PREFIX}cat`: 냐짤 수급

    """
    cat_say = functools.partial(
        bot.api.chat.postMessage,
        channel=event.channel,
        as_user=False,
        username='냥짤의 요정',
        icon_url='https://i.imgur.com/hIBJUMI.jpg',
    )

    now_dt = now()
    if event.channel.id in cat.last_call:
        last_call = cat.last_call[event.channel.id]
        if isinstance(event.channel, DirectMessageChannel):
            cooltime = DM_COOLTIME
        else:
            cooltime = DEFAULT_COOLTIME
        if now_dt - last_call < cooltime:
            fine = last_call + cooltime
            await cat_say(
                text=(
                    f'아직 쿨타임이다냥! ' f"{fine.strftime('%H시 %M분')} 이후로 다시 시도해보라냥!"
                )
            )
            return

    try:
        url = await get_cat_image_url(timeout)
    except APIServerError:
        await cat_say(text='냥냥이 API 서버의 상태가 좋지 않다냥! 나중에 다시 시도해보라냥!')
        return

    cat.last_call[event.channel.id] = now_dt

    await cat_say(text=url)


@box.command('dog', ['멍'])
@option('--timeout', default=1.5)
async def dog(bot, event: Message, timeout: float):
    """
    멍멍이 짤을 수급합니다.

    쿨타임은 일반 채널 30분, DM 3분입니다.

    `{PREFIX}dog`: 멍짤 수급

    """

    dog_say = functools.partial(
        bot.api.chat.postMessage,
        channel=event.channel,
        as_user=False,
        username='멍짤의 요정',
        icon_url='https://i.imgur.com/Q9FKplO.png',
    )

    now_dt = now()
    if event.channel.id in dog.last_call:
        last_call = dog.last_call[event.channel.id]
        if isinstance(event.channel, DirectMessageChannel):
            cooltime = DM_COOLTIME
        else:
            cooltime = DEFAULT_COOLTIME
        if now_dt - last_call < cooltime:
            fine = last_call + cooltime
            await dog_say(
                text=(
                    f'아직 쿨타임이다멍! ' f"{fine.strftime('%H시 %M분')} 이후로 다시 시도해보라멍!"
                )
            )
            return

    try:
        url = await get_dog_image_url(timeout)
    except APIServerError:
        await dog_say(text='멍멍이 API 서버의 상태가 좋지 않다멍! 나중에 다시 시도해보라멍!')
        return

    dog.last_call[event.channel.id] = now_dt

    await dog_say(text=url)


@box.command('fox', ['여우'])
async def fox(bot, event: Message, timeout: float = 1.5):
    """
    여우 짤을 수급합니다.

    쿨타임은 일반 채널 30분, DM 3분입니다.

    `{PREFIX}fox`: 여우짤 수급

    """

    fox_say = functools.partial(
        bot.api.chat.postMessage,
        channel=event.channel,
        as_user=False,
        username='웹 브라우저의 요정',
        icon_url='https://i.imgur.com/xFpyvpZ.png',
    )

    now_dt = now()
    if event.channel.id in fox.last_call:
        last_call = fox.last_call[event.channel.id]
        if isinstance(event.channel, DirectMessageChannel):
            cooltime = DM_COOLTIME
        else:
            cooltime = DEFAULT_COOLTIME
        if now_dt - last_call < cooltime:
            fine = last_call + cooltime
            await fox_say(
                text=(
                    f'아직 쿨타임이에요! ' f"{fine.strftime('%H시 %M분')} 이후로 다시 시도해보세요!"
                )
            )
            return

    try:
        url = await get_fox_image_url(timeout)
    except APIServerError:
        await fox_say(text='여우짤 서버의 상태가 좋지 않네요! 나중에 다시 시도해보세요!')
        return

    fox.last_call[event.channel.id] = now_dt

    await fox_say(text=url)
