from ...box import box
from ...event import Message

MESSAGE = """\
안녕하세요! 저는 유이라고 해요! <@item4>님이 만든 *다목적 Slack 봇* 이에요!
사람이 아니라 자동 응답 프로그램이에요.
유이의 명령어 목록은 `{prefix}도움` 을 입력하시면 보실 수 있어요.

금전적 후원(1회): https://www.buymeacoffee.com/item4
금전적 후원(구독): https://www.patreon.com/item4
기술적 후원: https://github.com/item4/yui

유이에게 많은 사랑과 관심 부탁드려요!

"""


@box.command("about", ["봇소개", "자기소개"])
async def about(bot, event: Message):
    """
    봇 소개

    `{PREFIX}about` (봇 소개)

    """

    await bot.say(
        event.channel,
        MESSAGE.format(prefix=bot.config.PREFIX),
        thread_ts=event.ts,
    )
