import aiohttp
import datetime
import json

from ..box import box
from ..event import Message
from ..util import static_vars


@box.command('cat')
@static_vars({'last_call': None})
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
        async with session.get('http://api.giphy.com/v1/gifs/random', params={
            'api_key': bot.config.GIPHY_API_KEY,
            'tag': 'cat',
        }) as resp:
            json_result = json.loads(await resp.read())
            url = json_result['data']['image_url']

            await bot.say(
                event.channel,
                url
            )
