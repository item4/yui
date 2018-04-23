import asyncio
import datetime
import functools

import aiohttp

import async_timeout

from lxml import etree

import ujson

import random

from ..box import box
from ..command import option
from ..event import Message
from ..session import client_session
from ..type import DirectMessageChannel
from ..util import now, static_vars

DEFAULT_COOLTIME = datetime.timedelta(minutes=30)
DM_COOLTIME = datetime.timedelta(minutes=3)


async def get_cat_image_url(timeout: float) -> str:
    api_url = 'http://thecatapi.com/api/images/get'
    async with client_session() as session:
        while True:
            try:
                async with session.get(api_url, params={
                    'format': 'xml',
                    'type': 'jpg,png',
                }) as res:
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
    async with client_session() as session:
        while True:
            try:
                async with session.get(api_url) as res:
                    data = await res.json(loads=ujson.loads)
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


@box.command('cat', ['냥', '야옹', '냐옹'])
@option('--timeout', default=1.5)
@static_vars(last_call={})
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

    lee_say = functools.partial(
        bot.api.chat.postMessage,
        channel=event.channel,
        as_user=False,
        username='Lee의 요정',
        icon_url='https://i.imgur.com/hIBJUMI.jpg',
        text='https://pbs.twimg.com/profile_images/756486934747242496/Y0VaYlyr.jpg'
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
                    f"아직 쿨타임이다냥! "
                    f"{fine.strftime('%H시 %M분')} 이후로 다시 시도해보라냥!"
                )
            )
            return

    cat.last_call[event.channel.id] = now_dt

    if random.randrange(3)%3 == 0:
        await lee_say()
    else:
        url = await get_cat_image_url(timeout)
        await cat_say(text=url)


@box.command('dog', ['멍'])
@option('--timeout', default=1.5)
@static_vars(last_call={})
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
                    f"아직 쿨타임이다멍! "
                    f"{fine.strftime('%H시 %M분')} 이후로 다시 시도해보라멍!"
                )
            )
            return

    dog.last_call[event.channel.id] = now_dt

    url = await get_dog_image_url(timeout)
    await dog_say(text=url)
