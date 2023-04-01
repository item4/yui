from ...box import box
from ...event import Message

box.assert_user_required("owner")


@box.command("quit")
async def quit(bot, event: Message):
    """
    봇을 종료합니다

    `{PREFIX}quit`

    봇 주인만 사용 가능합니다.

    """

    if event.user == bot.config.USERS["owner"]:
        await bot.say(event.channel, "안녕히 주무세요!")
        raise SystemExit
    await bot.say(
        event.channel,
        f"<@{event.user}> 이 명령어는 아빠만 사용할 수 있어요!",
    )
