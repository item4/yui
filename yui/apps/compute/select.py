import random
from typing import List

from ...box import box
from ...command import argument, option
from ...event import Message


@box.command('select', ['선택', '골라'])
@option('--seed')
@argument('items', nargs=-1)
async def select(bot, event: Message, items: List[str], seed: int):
    """
    주어진 항목중에 랜덤으로 선택해서 알려줍니다.

    `{PREFIX}선택 멍멍이 냐옹이` (멍멍이와 냐옹이중에 랜덤으로 선택)

    이 명령어는 `select`, `선택`, `골라` 중 편한 이름으로 사용할 수 있습니다.

    """

    random.seed(seed)

    await bot.say(
        event.channel,
        f'선택결과: {random.choice(items)}'
    )

    random.seed(None)
