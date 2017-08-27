from ..box import box
from ..event import Message

__all__ = 'ping',


@box.command('ping', ['핑'])
async def ping(bot, event: Message, user):
    """
    간단한 핑퐁

    `{PREFIX}ping`

    """

    await bot.say(
        event.channel,
        '@{}, pong!'.format(user['user']['name'])
    )
