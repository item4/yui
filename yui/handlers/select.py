import random

from ..box import box
from ..command import argument, option


@box.command('select', ['선택', '골라'])
@option('--sep', '-s', default=' ')
@argument('items', nargs=-1, concat=True)
async def select(bot, message, sep, items):
    """
    주어진 항목중에 랜덤으로 선택해서 알려줍니다.

    `{PREFIX}선택 멍멍이 냐옹이` (멍멍이와 냐옹이중에 랜덤으로 선택)
    `{PREFIX}선택 --sep=/ dog/cat/fish` (dog, cat, fish중에 랜덤으로 선택)

    이 명령어는 `select`, `선택`, `골라` 중 편한 이름으로 사용할 수 있습니다.

    """

    items = [x.strip() for x in items.split(sep)]

    await bot.say(
        message['channel'],
        random.choice(items)
    )
