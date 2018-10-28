import inspect
import math
from decimal import Decimal, InvalidOperation, ROUND_FLOOR

from scipy.stats import nbinom

from sympy.functions.combinatorial.numbers import harmonic


from ...box import box, route
from ...command import argument, option
from ...event import Message
from ...transform import value_range

SUCCESSES_MIN = 1
SUCCESSES_MAX = 10000
CHANCE_MIN = Decimal('0.00001')
CHANCE_MAX = Decimal('0.99')
CHANCES = [
    Decimal('0.25'),
    Decimal('0.5'),
    Decimal('0.75'),
    Decimal('0.95'),
    Decimal('0.99'),
]
D001 = Decimal('0.01')


def to_percent(v: Decimal, q=CHANCE_MIN) -> str:
    s = str((v * 100).quantize(q, rounding=ROUND_FLOOR))
    if '.' in s:
        return s.rstrip('0').rstrip('.')
    return s


class Gacha(route.RouteApp):

    def __init__(self) -> None:
        self.name = '가챠'
        self.route_list = [
            route.Route(name='수집', callback=self.collect),
            route.Route(name='collect', callback=self.collect),
            route.Route(name='도전', callback=self.challenge),
            route.Route(name='challenge', callback=self.challenge),
        ]

    def get_short_help(self, prefix: str):
        return f'`{prefix}가챠`: 가챠 계산기'

    def get_full_help(self, prefix: str):
        return inspect.cleandoc(f"""
        *가챠 계산기*

        해로운 문명, 가챠에 관련된 계산을 도와줍니다.

        `{prefix}가챠 수집 10` (총 10종류가 있는 요소를 구입하려면 몇 번 구입해야하는지 계산)
        `{prefix}가챠 도전 5%` (5% 확률요소의 성공을 위해 필요한 도전 횟수를 계산)
        `{prefix}가챠 도전 0.1` (10%(`0.1`) 확률요소의 성공을 위해 필요한 도전 횟수를 계산)
        `{prefix}가챠 도전 --성공 10 3%`""" + """\
        (3% 확률요소의 10회 성공을 위해 필요한 도전 횟수를 계산)

        Aliases

        - `수집`대신 `collect`를 사용할 수 있습니다.
        - `도전`대신 `challenge`를 사용할 수 있습니다.
        - `도전`에서 `--성공`대신 `--성공횟수`/`--successes`/`-s`를 사용할 수 있습니다.
        """)

    async def fallback(self, bot, event: Message):
        await bot.say(
            event.channel,
            f'Usage: `{bot.config.PREFIX}help 가챠`'
        )

    @option('--successes', '-s', '--성공횟수', '--성공', default=1)
    @argument('chance')
    async def challenge(
        self,
        bot,
        event: Message,
        successes: int,
        chance: str,
    ):
        if successes < SUCCESSES_MIN or successes > SUCCESSES_MAX:
            await bot.say(
                event.channel,
                f'성공횟수는 {SUCCESSES_MIN}회 이상,'
                f' {SUCCESSES_MAX:,}회 이하로 입력해주세요!'
            )
            return
        try:
            if chance.endswith('%'):
                p = Decimal(chance[:-1]) / 100
            else:
                p = Decimal(chance)
        except InvalidOperation:
            await bot.say(
                event.channel,
                '정상적인 확률을 입력해주세요!'
            )
            return
        if p < CHANCE_MIN or p > CHANCE_MAX:
            await bot.say(
                event.channel,
                f'확률값은 {to_percent(CHANCE_MIN)}% 이상,'
                f' {to_percent(CHANCE_MAX)}% 이하로 입력해주세요!'
            )
            return
        if p / successes < CHANCE_MIN:
            await bot.say(
                event.channel,
                '입력하신 확률값에 비해 성공 횟수가 너무 많아요!'
            )
            return
        counts = {
            int(math.ceil(
                nbinom.ppf(float(q), successes, float(p))
            ))
            for q in filter(lambda x: x >= p, CHANCES + [p])
        }
        results = [
            (x, Decimal(str(nbinom.cdf(x, successes, float(p)))))
            for x in sorted(counts)
        ]
        text = '\n'.join(
            f'- {tries+successes:,}번 시도하시면 {to_percent(ch, D001)}% 확률로'
            f' 목표 횟수만큼 성공할 수 있어요!'
            for tries, ch in results
        )
        await bot.say(
            event.channel,
            f'{to_percent(p)}% 확률의 도전을 {successes:,}번'
            f' 성공시키려면 몇 회의 도전이 필요한지 알려드릴게요!\n{text}'
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
