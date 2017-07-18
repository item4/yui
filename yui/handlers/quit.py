from ..box import box


@box.command('quit')
async def quit(bot, message, user):
    """
    봇을 종료합니다

    `{PREFIX}quit`

    봇 주인만 사용 가능합니다.

    """

    if message['user'] == bot.config.OWNER:
        await bot.say(message['channel'], '안녕히 주무세요!')
        raise SystemExit()
    else:
        await bot.say(
            message['channel'],
            '@{} 이 명령어는 아빠만 사용할 수 있어요!'.format(user['user']['name'])
        )
