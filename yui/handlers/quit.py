from ..box import box


@box.command('quit')
async def quit(bot, message, user):
    if message['user'] == bot.config.OWNER:
        await bot.say(message['channel'], '안녕히 주무세요!')
        raise SystemExit()
    else:
        await bot.say(
            message['channel'],
            '@{} 이 명령어는 아빠만 사용할 수 있어요!'.format(user['user']['name'])
        )
