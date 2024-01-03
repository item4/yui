from ....box import box
from ....event import Message
from .commons import say_d2r_terror_zone_info


@box.command("테러존", ["d2tz"])
async def d2r_terror_zone(bot, event: Message):
    """
    D2R 테러존 정보 조회

    디아블로 2 레저렉션의 공포의 영역(테러존)현황을 조회합니다.

    `{PREFIX}테러존` (테러존 현황)

    """

    await say_d2r_terror_zone_info(bot, event.channel)
