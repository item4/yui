from ..box import box

__all__ = 'ping',


@box.command('ping', ['핑'])
async def ping(bot, message, user):
    """
    간단한 핑퐁

    `{PREFIX}ping`

    """

    await bot.say(
        message['channel'],
        '@{}, pong!'.format(user['user']['name'])
    )
