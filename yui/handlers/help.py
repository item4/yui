from ..box import box
from ..event import Message


def make_inline_help_text(prefix, h):
    return (
        f'{"/".join(f"`{prefix}{n}`" for n in h.names)}:'
        f' {h.short_help}'
    )


@box.command('help', ['도움', '도움말'])
async def help(bot, event: Message, raw: str):
    """
    봇 명령어들의 도움말 모음

    `{PREFIX}help` (전체 명령어 목록)
    `{PREFIX}help quit` (개별 명령어 도움말)

    """

    if raw == '':
        await bot.say(
            event.channel,
            '\n'.join(
                make_inline_help_text(bot.config.PREFIX, h)
                for h in bot.box.handlers['message'][None]
                if h.is_command
            ),
            thread_ts=event.ts,
        )
    else:
        handlers = [
            h for h in bot.box.handlers['message'][None] if raw in h.names
        ]

        if handlers:
            await bot.say(
                event.channel,
                '\n'.join(
                    make_inline_help_text(bot.config.PREFIX, h)
                    for h in handlers
                ),
                thread_ts=event.ts,
            )
        else:
            await bot.say(
                event.channel,
                '그런 명령어는 없어요!',
                thread_ts=event.ts,
            )
