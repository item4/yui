from ..box import box


@box.command('help', ['도움', '도움말'])
async def help(bot, message, raw):
    """
    봇 명령어들의 도움말 모음

    `{PREFIX}help` (전체 명령어 목록)
    `{PREFIX}help quit` (개별 명령어 도움말)

    """

    if raw == '':
        await bot.say(
            message['channel'],
            '\n'.join(
                f'`{bot.config.PREFIX}{name}`: {h.short_help}'
                for name, h in bot.box.handlers['message'][None].items()
                if h.is_command
            ),
            thread_ts=message['ts'],
        )
    else:
        name = bot.box.aliases[None].get(raw, raw)
        handler = bot.box.handlers['message'][None].get(name)

        if handler:
            await bot.say(
                message['channel'],
                f'{handler.short_help}\n\n{handler.help}'.format(
                    PREFIX=bot.config.PREFIX
                ),
                thread_ts=message['ts'],
            )
        else:
            await bot.say(
                message['channel'],
                '그런 명령어는 없어요!',
                thread_ts=message['ts'],
            )
