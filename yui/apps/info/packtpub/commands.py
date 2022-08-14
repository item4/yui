from .commons import say_packtpub_dotd
from ....box import box
from ....event import Message


@box.command("무료책", ["freebook"])
async def packtpub_dotd(bot, event: Message):
    """
    PACKT Book 무료책 안내

    PACKT Book에서 날마다 무료로 배부하는 Deal of The Day를 조회합니다.

    `{PREFIX}무료책` (오늘의 무료책)

    """

    await say_packtpub_dotd(bot, event.channel)
