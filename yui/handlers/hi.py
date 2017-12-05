from ..box import box
from ..event import Message

__all__ = 'hi',


@box.on(Message)
async def hi(bot, event: Message):
    if event.text in ['안녕', '안녕 유이', '유이 안녕']:
        try:
            await bot.say(
                event.channel,
                '안녕하세요! @{}'.format(event.user.name)
            )
        except AttributeError:
            pass
        return False
    return True
