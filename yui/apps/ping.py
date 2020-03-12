from ..box import box
from ..event import Message


@box.command('ping', ['핑'])
async def ping(bot, event: Message):
    """
    간단한 핑퐁

    `{PREFIX}ping`

    """

    await bot.say(event.channel, '@{}, pong!'.format(event.user.name))
