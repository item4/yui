from ...box import box
from ...command import argument
from ...command import option
from ...event import Message
from ...transform import get_channel_id
from ...transform import get_user_id
from ...types.base import ChannelID
from ...types.base import UserID

box.assert_user_required("owner")


@box.command("say", aliases=["말", "말해"])
@option("--channel", "-c", transform_func=get_channel_id)
@option("--user", "-u", transform_func=get_user_id)
@argument("message", nargs=-1, concat=True)
async def say(
    bot,
    event: Message,
    channel: ChannelID | None,
    user: UserID | None,
    message: str,
):
    """
    봇이 말하게 합니다

    `{PREFIX}say payload` (현재 채널)
    `{PREFIX}say --channel=#test payload` (`#test` 채널)
    `{PREFIX}say --user=@admin payload` (`@admin` 유저)

    봇 주인만 사용 가능합니다.

    """
    target: ChannelID | UserID = event.channel
    if event.user == bot.config.USERS["owner"]:
        if channel and user:
            text = "`--channel` 옵션과 `--user` 옵션은 동시에 사용할 수 없어요!"
        else:
            text = message
            if channel:
                target = channel
            elif user:
                resp = await bot.api.conversations.open(users=[user])
                target = resp.body["channel"]["id"]
    else:
        text = f"<@{event.user}> 이 명령어는 아빠만 사용할 수 있어요!"

    await bot.say(
        target,
        text,
    )
