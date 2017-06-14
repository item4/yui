from ..box import box

__all__ = 'ping',


@box.command('ping', ['핑'])
async def ping(bot, message):
    user = await bot.api.users.info(message.get('user'))
    await bot.say(
        message['channel'],
        '@{}, pong!'.format(user['user']['name'])
    )
