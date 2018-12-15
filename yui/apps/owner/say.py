from typing import Optional

from ...box import box
from ...command import U, argument, option
from ...event import Message
from ...transform import get_channel, get_user
from ...types.channel import Channel
from ...types.user import User

box.assert_user_required('owner')


@box.command('say', aliases=['말', '말해'])
@option('--channel', '-c', transform_func=get_channel)
@option('--user', '-u', transform_func=get_user)
@argument('message', nargs=-1, concat=True)
async def say(
    bot,
    event: Message,
    channel: Optional[Channel],
    user: Optional[User],
    message: str,
):
    """
    봇이 말하게 합니다

    `{PREFIX}say payload` (현재 채널)
    `{PREFIX}say --channel=#test payload` (`#test` 채널)
    `{PREFIX}say --user=@admin payload` (`@admin` 유저)

    봇 주인만 사용 가능합니다.

    """

    target: Channel = event.channel
    if event.user == U.owner.get():
        if channel and user:
            text = '`--channel` 옵션과 `--user` 옵션은 동시에 사용할 수 없어요!'
        else:
            text = message
            if channel:
                target = channel
            elif user:
                resp = await bot.api.im.open(user)
                target = resp['channel']['id']
    else:
        text = '<@{}> 이 명령어는 아빠만 사용할 수 있어요!'.format(event.user.name)

    await bot.say(
        target,
        text,
    )
