import aiohttp
import datetime
from xml.etree import ElementTree

from ..box import box
from ..event import Message
from ..util import static_vars


@box.command('cat')
@static_vars(last_call=None)
async def nya(bot, event: Message, sess):
    cool_time = datetime.timedelta(minutes=10)
    now = datetime.datetime.utcnow()
    if nya.last_call is not None and now - nya.last_call < cool_time:
        bot.say(
            event.channel,
            '아직 쿨타임이다냥'
        )
        return

    nya.last_call = now

    async with aiohttp.ClientSession() as session:
        async with session.get('http://thecatapi.com/api/images/get', params={
            'format': 'xml',
        }) as resp:
            xml_result = await resp.read()
            tree = ElementTree.fromstring(xml_result)
            url = tree.find('data/images/image/url').text

            await bot.say(
                event.channel,
                url
            )
