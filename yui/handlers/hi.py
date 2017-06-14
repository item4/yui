from ..box import box

__all__ = 'hi',


@box.on('message')
async def hi(bot, message):
    if message['text'] in ['안녕', '안녕 유이', '유이 안녕']:
        user = await bot.api.users.info(message.get('user'))
        await bot.say(
            message['channel'],
            '안녕하세요! @{}'.format(user['user']['name'])
        )
        return False
    return True
