import inspect
import math
import re
from collections.abc import Callable
from decimal import Decimal
from decimal import InvalidOperation
from decimal import ROUND_FLOOR
from typing import Final

from scipy.stats import nbinom
from sympy.abc import x
from sympy.functions.combinatorial.numbers import harmonic
from sympy.utilities.lambdify import lambdify

from ...box import box
from ...box import route
from ...command import argument
from ...command import option
from ...event import Message

SUCCESSES_MIN: Final = 1
SUCCESSES_MAX: Final = 10000
CHANCE_MIN: Final = Decimal("0.00001")
CHANCE_MAX: Final = Decimal("0.99")
CHANCES: Final = (
    Decimal("0.25"),
    Decimal("0.5"),
    Decimal("0.75"),
    Decimal("0.95"),
    Decimal("0.99"),
)
D001: Final = Decimal("0.01")
COLLECT_QUERY1 = re.compile(r"^(?P<n>\d+)(?:\s*/\s*(?P<total>\d+))?$")
COLLECT_QUERY2 = re.compile(
    r"^(?:(?:총|전체)\s*)?"
    r"(?P<total>\d+)\s*(?:종류?|개)?\s*중(?:에서?)?\s*"
    r"(?P<n>\d+)\s*(?:종류?|개)?$",
)

collect_func: Callable[[int], float] = lambdify(
    x,
    x * harmonic(x),
    modules="sympy",
)


def to_percent(v: Decimal, q=CHANCE_MIN) -> str:
    s = str((v * 100).quantize(q, rounding=ROUND_FLOOR))
    if "." in s:
        return s.rstrip("0").rstrip(".")
    return s


class Gacha(route.RouteApp):
    def __init__(self) -> None:
        self.name = "가챠"
        self.route_list.extend(
            [
                route.Route(name="수집", callback=self.collect),
                route.Route(name="collect", callback=self.collect),
                route.Route(name="도전", callback=self.challenge),
                route.Route(name="challenge", callback=self.challenge),
            ],
        )

    def get_short_help(self, prefix: str):
        return f"`{prefix}가챠`: 가챠 계산기"

    def get_full_help(self, prefix: str):
        return inspect.cleandoc(
            f"""
*가챠 계산기*

해로운 문명, 가챠에 관련된 계산을 도와줍니다.

`{prefix}가챠 수집 10`
(총 10종을 모두 수집하려면 얼마나 구입해야하는지 계산)
`{prefix}가챠 수집 10/20`
(총 20종 중에 10종을 수집하려면 얼마나 구입해야하는지 계산)
`{prefix}가챠 수집 전체 20종류중에 10종류`
(위와 동일한 주문을 한국어 표현식으로도 가능합니다.)
`{prefix}가챠 도전 5%`
(5% 확률요소의 성공을 위해 필요한 도전 횟수를 계산)
`{prefix}가챠 도전 0.1`
(10%(`0.1`) 확률요소의 성공을 위해 필요한 도전 횟수를 계산)
`{prefix}가챠 도전 --성공 10 3%`
(3% 확률요소의 10회 성공을 위해 필요한 도전 횟수를 계산)

Aliases

- `수집`대신 `collect`를 사용할 수 있습니다.
- `도전`대신 `challenge`를 사용할 수 있습니다.
- `도전`에서 `--성공`대신 `--성공횟수`/`--successes`/`-s`를 사용할 수 있습니다.
""",
        )

    async def fallback(self, bot, event: Message):
        await bot.say(event.channel, f"Usage: `{bot.config.PREFIX}help 가챠`")

    @option("--successes", "-s", "--성공횟수", "--성공", default=1)
    @argument("chance")
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
                f"성공횟수는 {SUCCESSES_MIN}회 이상, {SUCCESSES_MAX:,}회"
                " 이하로 입력해주세요!",
            )
            return
        try:
            p = (
                Decimal(chance[:-1]) / 100
                if chance.endswith("%")
                else Decimal(chance)
            )
        except InvalidOperation:
            await bot.say(event.channel, "정상적인 확률을 입력해주세요!")
            return
        if p < CHANCE_MIN or p > CHANCE_MAX:
            await bot.say(
                event.channel,
                f"확률값은 {to_percent(CHANCE_MIN)}% 이상,"
                f" {to_percent(CHANCE_MAX)}% 이하로 입력해주세요!",
            )
            return
        if p / successes < CHANCE_MIN:
            await bot.say(
                event.channel,
                "입력하신 확률값에 비해 성공 횟수가 너무 많아요!",
            )
            return
        counts = {
            math.ceil(nbinom.ppf(float(q), successes, float(p)))
            for q in filter(lambda x: x >= p, [*CHANCES, p])
        }
        results = [
            (x, Decimal(str(nbinom.cdf(x, successes, float(p)))))
            for x in sorted(counts)
        ]
        text = "\n".join(
            f"- {tries + successes:,}번 시도하시면"
            f" {to_percent(ch, D001)}% 확률로"
            " 목표 횟수만큼 성공할 수 있어요!"
            for tries, ch in results
        )
        await bot.say(
            event.channel,
            f"{to_percent(p)}% 확률의 도전을 {successes:,}번"
            f" 성공시키려면 몇 회의 도전이 필요한지 알려드릴게요!\n{text}",
        )

    @argument("query", nargs=-1, concat=True)
    async def collect(self, bot, event: Message, query: str):
        match = COLLECT_QUERY1.match(query)
        if match:
            n = int(match.group("n"))
            total = int(match.group("total")) if match.group("total") else n
        else:
            match = COLLECT_QUERY2.match(query)
            if match:
                n = int(match.group("n"))
                total = int(match.group("total"))
            else:
                await bot.say(event.channel, "요청을 해석하는데에 실패했어요!")
                return
        if total < 2 or total > 512:
            await bot.say(
                event.channel,
                "정상적인 전체 갯수를 입력해주세요! (2개 이상 512개 이하)",
            )
            return
        if n < 1 or n > 512:
            await bot.say(
                event.channel,
                "정상적인 수집 갯수를 입력해주세요! (1개 이상 512개 이하)",
            )
            return
        if total < n:
            await bot.say(
                event.channel,
                "원하는 갯수가 전체 갯수보다 많을 수 없어요!",
            )
            return

        result = collect_func(n)
        if total > n:
            result /= n / total
            text = "부분적으로"
        else:
            text = "모두"

        await bot.say(
            event.channel,
            f"상품 1개 구입시 {total}종류의 특전 중 하나를 무작위로 100%"
            f"확률로 준다고 가정할 때 {n}종류의 특전을"
            f" {text} 모으려면, 평균적으로"
            f" {math.ceil(result)}(`{float(result):.2f}`)개의 상품을"
            " 구입해야 수집에 성공할 수 있어요!",
        )


box.register(Gacha())
