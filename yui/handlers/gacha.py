import inspect
import math

from sympy.functions.combinatorial.numbers import harmonic


from ..box import CommandMappingHandler, CommandMappingUnit, box
from ..command import argument
from ..event import Message
from ..transform import value_range


class Gacha(CommandMappingHandler):

    def __init__(self) -> None:
        self.name = '가챠'
        self.command_map = [
            CommandMappingUnit(name='수집', callback=self.collect),
            CommandMappingUnit(name='collect', callback=self.collect),
        ]

    def get_short_help(self, prefix: str):
        return f'`{prefix}가챠`: 가챠 계산기'

    def get_full_help(self, prefix: str):
        return inspect.cleandoc(f"""
        *가챠 계산기*

        해로운 문명, 가챠에 관련된 계산을 도와줍니다.

        `{prefix}가챠 수집 10` (총 10종류가 있는 요소를 구입하려면 몇 번 구입해야하는지 계산)

        `수집` 대신 `collect` 를 사용할 수 있습니다.""")

    async def fallback(self, bot, event: Message):
        await bot.say(
            event.channel,
            f'Usage: `{bot.config.PREFIX}help 가챠`'
        )

    @argument('n', type_=int, transform_func=value_range(1, 128),
              transform_error='특전 종류는 1개 이상 128개 이하로 해주세요!')
    async def collect(self, bot, event: Message, n: int):
        result = n * harmonic(n)

        await bot.say(
            event.channel,
            f'상품 1개 구입시 {n}종류의 특전 중 하나를 무작위로 100% 확률로 준다고 가정할 때'
            f' {n}종류의 특전을 모두 모으려면, 평균적으로 {math.ceil(result)}'
            f'(`{float(result):.2f}`)개의 상품을 구입해야 전체 수집에 성공할 수 있어요!'
        )


box.register(Gacha())
