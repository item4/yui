import aiohttp
import datetime
from lxml import etree

from ..box import box
from ..event import Message
from ..util import static_vars


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
        bot.say(
            event.channel,
            '아직 쿨타임이다냥'
        )
        return

    cat.last_call = now

    async with aiohttp.ClientSession() as session:
        async with session.get('http://thecatapi.com/api/images/get', params={
            'format': 'xml',
        }) as resp:
            xml_result = await resp.read()
            tree = etree.fromstring(xml_result)
            url = tree.find('data/images/image/url').text

            await bot.say(
                event.channel,
                url
            )
