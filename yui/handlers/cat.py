import datetime

import aiohttp

from lxml import etree

from ..box import box
from ..event import Message
from ..util import static_vars


async def get_cat_image_url() -> str:
    api_url = 'http://thecatapi.com/api/images/get'
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(api_url, params={
                'format': 'xml',
                'type': 'jpg,png',
            }) as res:
                xml_result = await res.read()
                tree = etree.fromstring(xml_result)
                url = tree.find('data/images/image/url').text
            async with session.get(url) as res:
                if res.status == 200:
                    return url


@box.command('cat')
@static_vars(last_call=None)
async def cat(bot, event: Message, sess):
    """
    냥냥이 짤을 수급합니다.
    쿨타임은 10분입니다.

    `{PREFIX}cat`: 냐짤 수급
    """

    cool_time = datetime.timedelta(minutes=10)
    now = datetime.datetime.utcnow()
    if cat.last_call is not None and now - cat.last_call < cool_time:
        await bot.say(
            event.channel,
            '아직 쿨타임이다냥'
        )
        return

    cat.last_call = now

    url = await get_cat_image_url()
    await bot.say(
        event.channel,
        url
    )
